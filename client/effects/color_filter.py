from typing import Optional
import cv2
import numpy as np
from effects.ieffect import IEffect
from colors import Colors

class ColorFilter(IEffect):
    def __init__(self):
        pass

    def apply(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if frame is None:
            return None
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        yellow_mask = self.create_color_mask(hsv, "yellow")
        red_mask = self.create_color_mask(hsv, "red")
        green_mask = self.create_color_mask(hsv, "green")

        result = np.zeros_like(frame)

        result[yellow_mask == 255] = Colors.YELLOW_BGR
        result[red_mask == 255]   = Colors.RED_BGR
        result[green_mask == 255] = Colors.GREEN_BGR

        return result

    def create_mask(self, hsv: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
        return cv2.inRange(hsv, lower, upper)

    def create_color_mask(self, hsv: np.ndarray, color: str) -> np.ndarray:
        if color == "yellow":
            return self.create_mask(hsv, Colors.YELLOW_LOWER, Colors.YELLOW_UPPER)
        elif color == "red":
            red_mask1 = self.create_mask(hsv, Colors.RED_LOWER1, Colors.RED_UPPER1)
            red_mask2 = self.create_mask(hsv, Colors.RED_LOWER2, Colors.RED_UPPER2)
            return cv2.bitwise_or(red_mask1, red_mask2)
        elif color == "green":
            return self.create_mask(hsv, Colors.GREEN_LOWER, Colors.GREEN_UPPER)
        else:
            return np.zeros_like(hsv)
