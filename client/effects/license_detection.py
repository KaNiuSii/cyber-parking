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

ACCEPTED_FORMAT = re.compile(r'^[A-Z]{3}\d{4}$')
NOT_DETECTED_BUFFER = 10

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
            final_license_plate = self.get_license_plate()
            if operatingMode.enterance == self.operatingMode:
                processed_data.enterance_license_plates.append(final_license_plate)
            else:
                processed_data.exit_license_plates.append(final_license_plate)
                
            print("\n\n Final License Plate:", final_license_plate.number, "Arrival Time:", final_license_plate.arrival_time, "\n\n")
        
        if self.checkForRedOnScreen(frame) is False:
            return DataFrame(frame=frame, data=processed_data)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dark_mask = self.create_dark_mask(hsv)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        cv2.imshow('Dark Mask', dark_mask)

        detected_frame, license_plate_text = self.detect_license_plate(frame, dark_mask)

        if not license_plate_text:
            print("No text detected. Skipping frame.")
            return DataFrame(frame=frame, data=processed_data)

        processed_license_plate_text = self.process_license_plate(license_plate_text)
        
        self.detectionsHistory.append(processed_license_plate_text)
        self.lastFrameWithDetection = self.frameCounter

        print("Detected License Plate Text:", processed_license_plate_text, " Plate before processing:", license_plate_text)

        return DataFrame(frame=detected_frame, data=processed_data)

    def create_dark_mask(self, hsv: np.ndarray) -> np.ndarray:
        lower_bound = np.array([0, 0, 0], dtype=np.uint8)
        upper_bound = np.array([180, 255, 40], dtype=np.uint8)
        return cv2.inRange(hsv, lower_bound, upper_bound)
    

    def detect_license_plate(self, frame: np.ndarray, dark_mask: np.ndarray):
        masked_frame = cv2.bitwise_and(frame, frame, mask=dark_mask)

        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return frame, ""

        gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)

        results = self.reader.readtext(gray)

        license_plate_text = " ".join([res[1] for res in results])

        return masked_frame, license_plate_text
    
    def checkForRedOnScreen(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        return cv2.countNonZero(mask) > 100 
    
    def process_license_plate(self, license_plate_text: str) -> str:
        text_upper = license_plate_text.upper()
    
        letters = [c for c in text_upper if c.isalpha()]
        digits = [c for c in text_upper if c.isdigit()]
    
        letters_part = letters[:3]
        letters_str = ''.join(letters_part) + '?' * (3 - len(letters_part))
    
        digits_part = digits[:4]
        digits_str = ''.join(digits_part) + '?' * (4 - len(digits_part))
    
        return f"{letters_str} {digits_str}"
    
    def check_for_detection_timeout(self) -> bool:
        if self.frameCounter - self.lastFrameWithDetection > NOT_DETECTED_BUFFER and self.detectionsHistory:
            return True
        return False
            
    def get_license_plate(self) -> LicensePlate:
        if not self.detectionsHistory:
            return None
        
        print("License Plate History:", self.detectionsHistory)
        
        counts = defaultdict(int)
        for entry in self.detectionsHistory:
            counts[entry] += 1

        groups = defaultdict(list)
        for entry, count in counts.items():
            num_q = entry.count('?')
            sum_q_pos = sum(i for i, c in enumerate(entry) if c == '?')
            groups[num_q].append((entry, count, sum_q_pos))

        for num_q in sorted(groups.keys()):
            candidates = groups[num_q]
            # Sort candidates by:
            # 1. Frequency (descending)
            # 2. Sum of question mark positions (descending, to prioritize later positions)
            # 3. Lexicographical order (ascending) to break ties
            sorted_candidates = sorted(candidates, key=lambda x: (-x[1], -x[2], x[0]))
            if sorted_candidates:
                license_plate_text = sorted_candidates[0][0]
                break
        
        self.detectionsHistory = []
        
        return LicensePlate(number=license_plate_text, arrival_time=datetime.now())