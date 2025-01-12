from typing import List, Optional
import cv2
import numpy as np
from effects.ieffect import IEffect
from colors import Colors
from models.data_frame import DataFrame
from models.data import Data, CarPosition
from consts import Consts


class CarPositions(IEffect):
    def apply(self, frame: Optional[np.ndarray], dataframes: List[DataFrame]) -> DataFrame:
        if frame is None:
            raise ValueError("Frame is None. Cannot process.")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask1 = self.create_mask(hsv, Colors.RED_LOWER1, Colors.RED_UPPER1)
        red_mask2 = self.create_mask(hsv, Colors.RED_LOWER2, Colors.RED_UPPER2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        detected_frame, car_positions = self.detect_car_positions(frame, red_mask)

        updated_data = dataframes[-1]
        updated_data.data.car_positions = car_positions

        return DataFrame(frame=detected_frame, data=updated_data.data)

    def create_mask(self, hsv: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
        return cv2.inRange(hsv, lower, upper)

    def detect_car_positions(self, frame: np.ndarray, red_mask: np.ndarray):
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        car_positions = []

        for contour in contours:
            if cv2.contourArea(contour) > 1500 and cv2.contourArea(contour) < 4000:
                x, y, w, h = cv2.boundingRect(contour)
                car_position = CarPosition(name=Consts.UNKNOWN, x=x + w // 2, y=y + h // 2, w=w, h=h)
                car_positions.append(car_position)

        return frame, car_positions
