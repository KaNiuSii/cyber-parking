from typing import List, Optional
import cv2
import numpy as np
import re
from datetime import datetime
from easyocr import Reader
from effects.ieffect import IEffect
from collections import defaultdict
from models.data_frame import DataFrame
from models.license_plate import LicensePlate
from enum import Enum
from video_processor.data_holder import DataHolder

ACCEPTED_FORMAT = re.compile(r'^[A-Z]{3}\d{4}$')
NOT_DETECTED_BUFFER = 10
IGNORE_READINGS = {
    "IPL ",
    "IPl ",
    "IpL ",
    "Ipl ",
    "PL ",
    "Pl ",
    "pL ",
    "pl ",
}

class operatingMode(Enum):
    enterance = 1
    exit = 2

    
class LicenseDetector(IEffect):
    def __init__(self, operatingMode = operatingMode.enterance):
        self.reader = Reader(['en'], gpu=True)
        self.frameCounter = 0
        self.detectionsHistory = []
        self.lastFrameWithDetection = 0
        self.operatingMode = operatingMode
        
    def apply(self, frame: Optional[np.ndarray], dataframes: List[DataFrame]) -> DataFrame:
        if frame is None:
            raise ValueError("Frame is None. Cannot process.")
        
        processed_data = dataframes[-1].data
        self.frameCounter += 1
        
        if self.check_for_detection_timeout():
            final_license_plate = self.get_final_license_plate()
            if operatingMode.enterance == self.operatingMode and final_license_plate is not None:
                processed_data.enterance_license_plates.append(final_license_plate)
                print("\n\n Final License Plate:", final_license_plate.number, "Arrival Time:", final_license_plate.arrival_time, "\n\n")
            elif operatingMode.exit == self.operatingMode and final_license_plate is not None:
                processed_data.exit_license_plates.append(final_license_plate)
                print("\n\n Final License Plate:", final_license_plate.number, "Exit Time:", final_license_plate.arrival_time, "\n\n")
            
        
        if self.checkForRedOnScreen(frame) is False:
            return DataFrame(frame=frame, data=processed_data)
        
        roi = find_combined_roi(frame, debug_mode=True)
        cropped_image = frame
        
        if roi is not None:
            x1, y1, x2, y2 = roi
            cropped_image = frame[y1:y2, x1:x2]
            # cv2.imshow('ROI', cropped_image)
        else: 
            return DataFrame(frame=roi, data=processed_data)

        license_plate_text = self.detect_license_plate(cropped_image)

        if not license_plate_text:
            return DataFrame(frame=frame, data=processed_data)

        processed_license_plate_text = self.process_license_plate_text(license_plate_text)
        
        self.detectionsHistory.append(processed_license_plate_text)
        self.lastFrameWithDetection = self.frameCounter

        print("Detected License Plate Text:", processed_license_plate_text, " Plate before processing:", license_plate_text)

        if self.operatingMode == operatingMode.enterance:
            DataHolder.add(processed_license_plate_text)

        return DataFrame(frame=frame, data=processed_data)
    

    def detect_license_plate(self, roi: np.ndarray):
        results = self.reader.readtext(roi)

        license_plate_text = " ".join([res[1] for res in results])

        return license_plate_text
    
    def checkForRedOnScreen(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 80, 50), (15, 255, 255)) | cv2.inRange(hsv, (160, 80, 50), (180, 255, 255))
        # MANUAL AREA THRESHOLD
        return cv2.countNonZero(mask) > 1000
    
    def process_license_plate_text(self, license_plate_text: str) -> str:
        for reading in IGNORE_READINGS:
            if reading in license_plate_text:
                license_plate_text = license_plate_text.replace(reading, "")
        
        text_upper = re.sub("[a-z]", "", license_plate_text)
    
        letters = [c for c in text_upper if c.isalpha()]
        digits = [c for c in text_upper if c.isdigit()]
        
        if len(letters) > 3:
            letters_before_space = text_upper.split(' ')[0]
            if len(letters_before_space) > 3:
                letters = 3 * ['?']
                
        if len(digits) > 4:
            digits_after_space = text_upper.split(' ')[1]
            if len(digits_after_space) > 4:
                digits = 4 * ['?']
    
        letters_part = letters[:3]
        letters_str = ''.join(letters_part) + '?' * (3 - len(letters_part))
    
        digits_part = digits[:4]
        digits_str = ''.join(digits_part) + '?' * (4 - len(digits_part))
    
        return f"{letters_str} {digits_str}"
    
    def check_for_detection_timeout(self) -> bool:
        if self.frameCounter - self.lastFrameWithDetection > NOT_DETECTED_BUFFER and self.detectionsHistory:
            return True
        return False
            
    def get_final_license_plate(self) -> LicensePlate:
        if not self.detectionsHistory or len(self.detectionsHistory) < 5:
            return None
        
        print("License Plate History:", self.detectionsHistory)
        
        first_part = [entry[:3] for entry in self.detectionsHistory]
        second_part = [entry[4:] for entry in self.detectionsHistory]
        
        license_plate_text = get_best_reading(first_part) + ' ' + get_best_reading(second_part)
        
        self.detectionsHistory = []
        
        return LicensePlate(number=license_plate_text, arrival_time=datetime.now())
    
def get_best_reading(readings : List[str]) -> str:
    counts = defaultdict(int)
    for entry in readings:
        counts[entry] += 1

    groups = defaultdict(list)
    for entry, count in counts.items():
        num_q = entry.count('?')
        sum_q_pos = sum(i for i, c in enumerate(entry) if c == '?')
        groups[num_q].append((entry, count, sum_q_pos))

    for num_q in sorted(groups.keys()):
        candidates = groups[num_q]
        sorted_candidates = sorted(candidates, key=lambda x: (-x[1], -x[2], x[0]))
        if sorted_candidates:
            best_reading = sorted_candidates[0][0]
            break
    
    return best_reading

    
def find_combined_roi(image , debug_mode=False):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    red_mask = cv2.inRange(hsv, (0, 80, 50), (15, 255, 255)) | cv2.inRange(hsv, (160, 80, 50), (180, 255, 255))
    #white_mask = cv2.inRange(image, (200, 200, 200), (255, 255, 255))
    
    cv2.imshow('red_mask', red_mask)
    #cv2.imshow('white_mask', white_mask)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
    #combined_mask = cv2.bitwise_or(red_mask, white_mask)
    combined_mask = red_mask
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    #IMAGE TRIMMING
    #trim pixels from the bottom
    # combined_mask[-200:] = 0
    #trim pixels from the top
    # combined_mask[:200] = 0
    #trim pixels from the left
    # combined_mask[:, :200] = 0
    # trim pixels from the right
    # combined_mask[:, -100:] = 0

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None

    h, w = image.shape[:2]
    center = np.array([w//2, h//2])
    
    best_extremes = None
    min_center_distance = float('inf')
    
    for cnt in contours:
        # MANUAL AREA THRESHOLD
        # skip contours with area less than:
        if cv2.contourArea(cnt) < 500:
            continue
        
        extremes = get_extreme_points(cnt)
        
        cnt_center = np.mean(extremes, axis=0)
        distance = np.linalg.norm(cnt_center - center)
        
        if distance < min_center_distance:
            min_center_distance = distance
            best_extremes = extremes
    
    if best_extremes is None:
        return None
    
    x_coords = best_extremes[:, 0]
    y_coords = best_extremes[:, 1]
    
    x1 = max(0, np.min(x_coords))
    y1 = max(0, np.min(y_coords))
    x2 = min(w, np.max(x_coords))
    y2 = min(h, np.max(y_coords))
    
    if x2 <= x1 or y2 <= y1:
        return None
    
    if debug_mode:
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return (x1, y1, x2, y2)

def get_extreme_points(contour):
    points = contour.squeeze()
    
    if len(points.shape) < 2:
        return np.array([points, points, points, points])
    
    leftmost = points[np.argmin(points[:, 0])]
    rightmost = points[np.argmax(points[:, 0])]
    topmost = points[np.argmin(points[:, 1])]
    bottommost = points[np.argmax(points[:, 1])]
    
    return np.array([leftmost, rightmost, topmost, bottommost])
