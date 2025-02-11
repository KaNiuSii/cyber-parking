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

        any_but_parking_mask1 = self.create_mask(hsv, 0, 20)
        any_but_parking_mask2 = self.create_mask(hsv, 170, 180)
        any_but_parking_mask = cv2.bitwise_or(any_but_parking_mask1, any_but_parking_mask2)
        any_but_parking_mask = cv2.morphologyEx(any_but_parking_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        # cv2.imshow('co widzi bez parkingu', any_but_parking_mask)

        detected_frame, car_positions = self.detect_car_positions(frame, any_but_parking_mask)

        updated_data = dataframes[-1]
        updated_data.data.car_positions = car_positions

        return DataFrame(frame=detected_frame, data=updated_data.data)

    def create_mask(self, hsv: np.ndarray, h_lower: int, h_upper: int) -> np.ndarray:
        if h_lower <= h_upper:
            lower_bound = np.array([h_lower, 150, 150], dtype=np.uint8)
            upper_bound = np.array([h_upper, 255, 255], dtype=np.uint8)
            return cv2.inRange(hsv, lower_bound, upper_bound)
        else:
            lower_bound1 = np.array([h_lower, 150, 150], dtype=np.uint8)
            upper_bound1 = np.array([180, 255, 255], dtype=np.uint8)
            lower_bound2 = np.array([0, 150, 150], dtype=np.uint8)
            upper_bound2 = np.array([h_upper - 180, 255, 255], dtype=np.uint8)
            mask1 = cv2.inRange(hsv, lower_bound1, upper_bound1)
            mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
            return cv2.bitwise_or(mask1, mask2)


    def detect_car_positions(self, frame: np.ndarray, red_mask: np.ndarray):
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        car_positions = []

        for contour in contours:
            if cv2.contourArea(contour) > 500 and cv2.contourArea(contour) < 5000:
                x, y, w, h = cv2.boundingRect(contour)
                car_position = CarPosition(name=Consts.UNKNOWN, x=x + w // 2, y=y + h // 2, w=w, h=h)
                car_positions.append(car_position)

        return frame, car_positions
