from typing import List, Optional
import cv2
import numpy as np
from easyocr import Reader
from effects.ieffect import IEffect
from colors import Colors
from models.data_frame import DataFrame
from models.data import Data, CarPosition
from consts import Consts

class OCR(IEffect):
    def __init__(self):
        self.reader = Reader(['en'], gpu=True)  # Initialize EasyOCR reader
        self.xd = 0

    def apply(self, frame: Optional[np.ndarray], dataframes: List[DataFrame]) -> DataFrame:
        if frame is None:
            raise ValueError("Frame is None. Cannot process.")
        if self.xd % 10 != 0:
            self.xd += 1
            updated_data = dataframes[-1]  # Assume using the latest dataframe
            return DataFrame(frame=frame, data=updated_data.data)
        self.xd += 1

        # Convert to HSV and create a dark mask
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dark_mask = self.create_dark_mask(hsv)

        # Improve the mask using morphological operations
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        # Debug display
        cv2.imshow('Dark Mask', dark_mask)

        # Detect license plate text
        detected_frame, license_plate_text = self.detect_license_plate(frame, dark_mask)

        # If no license plate text is detected, skip processing
        if not license_plate_text:
            print("No text detected. Skipping frame.")
            updated_data = dataframes[-1]
            return DataFrame(frame=frame, data=updated_data.data)

        # Print recognized text
        print("Detected License Plate Text:", license_plate_text)

        # Update the data frame with the detected frame
        updated_data = dataframes[-1]
        return DataFrame(frame=detected_frame, data=updated_data.data)

    def create_dark_mask(self, hsv: np.ndarray) -> np.ndarray:
        # Threshold for dark areas (low V values in HSV)
        lower_bound = np.array([0, 0, 0], dtype=np.uint8)  # Minimum H, S, V
        upper_bound = np.array([180, 255, 40], dtype=np.uint8)  # Max H, max S, low V threshold
        return cv2.inRange(hsv, lower_bound, upper_bound)
    

    def detect_license_plate(self, frame: np.ndarray, dark_mask: np.ndarray):
        # Apply the mask to extract the region of interest (ROI)
        masked_frame = cv2.bitwise_and(frame, frame, mask=dark_mask)

        # Find contours to check for regions of interest
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Skip if no contours are found
        if not contours:
            return frame, ""  # Return original frame and empty text

        # Convert ROI to grayscale for OCR
        gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)

        # Use EasyOCR to detect text
        results = self.reader.readtext(gray)

        # Concatenate detected text
        license_plate_text = " ".join([res[1] for res in results])

        return masked_frame, license_plate_text
