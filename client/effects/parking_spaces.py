from typing import List, Optional
import cv2
import numpy as np
from effects.ieffect import IEffect
from colors import Colors
from models.data_frame import DataFrame
from models.data import Data, ParkingSpace


class ParkingSpaces(IEffect):
    def apply(self, frame: Optional[np.ndarray], dataframes: List[DataFrame]) -> DataFrame:
        if frame is None:
            raise ValueError("Frame is None. Cannot process.")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        green_mask = self.create_mask(hsv, 35, 85)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        # cv2.imshow('Parking spaces', green_mask)

        detected_parking_spaces = self.detect_parking_spaces(frame, green_mask)

        updated_data = dataframes[-1]
        updated_data.data.parking_spaces = detected_parking_spaces

        return DataFrame(frame=frame, data=updated_data.data)

    def create_mask(self, hsv: np.ndarray, h_lower: int, h_upper: int) -> np.ndarray:
        if h_lower <= h_upper:
            lower_bound = np.array([h_lower, 100, 100], dtype=np.uint8)
            upper_bound = np.array([h_upper, 255, 255], dtype=np.uint8)
            return cv2.inRange(hsv, lower_bound, upper_bound)
        else:
            lower_bound1 = np.array([h_lower, 0, 0], dtype=np.uint8)
            upper_bound1 = np.array([180, 255, 255], dtype=np.uint8)
            lower_bound2 = np.array([0, 0, 0], dtype=np.uint8)
            upper_bound2 = np.array([h_upper - 180, 255, 255], dtype=np.uint8)
            mask1 = cv2.inRange(hsv, lower_bound1, upper_bound1)
            mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
            return cv2.bitwise_or(mask1, mask2)

    def detect_parking_spaces(self, frame: np.ndarray, green_mask: np.ndarray) -> List[ParkingSpace]:
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        parking_spaces = []

        for contour in contours:
            if cv2.contourArea(contour) > 140:
                x, y, w, h = cv2.boundingRect(contour)
                position = (x + w // 2, y + h // 2)

                parking_spaces.append(ParkingSpace(id=len(parking_spaces) + 1, x=position[0], y=position[1], w=w, h=h))

                cv2.rectangle(frame, (x, y), (x + w, y + h), Colors.GREEN_BGR, 2)
                cv2.putText(frame, f"Space_{len(parking_spaces)}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, Colors.GREEN_BGR, 2)

        return parking_spaces
