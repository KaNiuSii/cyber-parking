from typing import Optional
import cv2
import numpy as np
from effects.ieffect import IEffect
from colors import Colors

class ParkingSpaces(IEffect):
    def __init__(self):
        pass

    def apply(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if frame is None:
            return None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        green_mask = self.create_mask(hsv, Colors.GREEN_LOWER, Colors.GREEN_UPPER)

        return self.detect_parking_spaces(frame, green_mask)

    def create_mask(self, hsv: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
        return cv2.inRange(hsv, lower, upper)

    def detect_parking_spaces(self, frame: np.ndarray, green_mask: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 2500:
                x, y, w, h = cv2.boundingRect(contour)
                position = (x + w // 2, y + h // 2)

                cv2.rectangle(frame, (x, y), (x + w, y + h), Colors.PURPLE_BGR, 2)
                cv2.putText(frame, f"{position}", (x, y + h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, Colors.PURPLE_BGR, 1, cv2.LINE_AA)

        return frame
