import re
import cv2
import easyocr
from datetime import datetime
from typing import List, Optional
import numpy as np
from effects.ieffect import IEffect
from models.data_frame import DataFrame
from models.license_plate import LicensePlate


class LicensePlateDetector(IEffect):
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.detected_plates = set()
        self.frame_counter = 0
        self.process_every_n_frames = 5

    def apply(self, frame: Optional[np.ndarray], dataframes: List[DataFrame]) -> DataFrame:
        if frame is None:
            return dataframes[-1]

        self.frame_counter += 1
        if self.frame_counter % self.process_every_n_frames != 0:
            return dataframes[-1]

        texts = self.detect_text(frame)
        filtered_plates = []

        for text in texts:
            if self.filter_license_plate(text):
                self.detected_plates.add(text)
                plate = LicensePlate(
                    number=text,
                    arrival_time=datetime.now(),
                    confidence=0.9
                )
                filtered_plates.append(plate)

        print("\nCurrent detection:", texts)
        print("All detected plates:", sorted(list(self.detected_plates)))
        print("Total unique plates:", len(self.detected_plates))

        updated_data = dataframes[-1]
        updated_data.data.license_plates = filtered_plates
        return DataFrame(frame=frame, data=updated_data.data)

    def detect_text(self, frame: np.ndarray) -> List[str]:
        results = self.reader.readtext(frame)
        plates = []

        if len(results) >= 2:
            for i in range(len(results) - 1):
                text1 = results[i][1].strip().upper()
                text2 = results[i + 1][1].strip().upper()

                if len(text1) == 3 and len(text2) == 4 and text2.isdigit():
                    plates.append(f"{text1} {text2}")

        return plates

    def filter_license_plate(self, text: str) -> bool:
        text = text.strip().upper()
        return bool(re.match(r'^[A-Z]{3}\s\d{4}$', text))