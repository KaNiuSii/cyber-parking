from typing import Optional
import cv2
import numpy as np
from effects.ieffect import IEffect
from colors import Colors

class CarPositions(IEffect):
    def __init__(self):
        pass

    def apply(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if frame is None:
            return None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask1 = self.create_mask(hsv, Colors.RED_LOWER1, Colors.RED_UPPER1)
        red_mask2 = self.create_mask(hsv, Colors.RED_LOWER2, Colors.RED_UPPER2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        return self.detect_car_positions(frame, red_mask)

    def create_mask(self, hsv: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
        return cv2.inRange(hsv, lower, upper)

    def detect_car_positions(self, frame: np.ndarray, red_mask: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 2500:
                x, y, w, h = cv2.boundingRect(contour)
                car_position = (x + w // 2, y + h // 2)

                cv2.rectangle(frame, (x, y), (x + w, y + h), Colors.PURPLE_BGR, 2)
                cv2.putText(frame, f"Position: {car_position}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, Colors.PURPLE_BGR, 2, cv2.LINE_AA)

        return frame
