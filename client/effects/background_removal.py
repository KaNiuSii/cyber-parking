from typing import Optional
import cv2
import numpy as np
from effects.ieffect import IEffect

class BackgroundRemoval(IEffect):
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    def apply(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if frame is None:
            return None

        fg_mask = self.bg_subtractor.apply(frame)
        
        fg_mask = cv2.medianBlur(fg_mask, 5)

        foreground = cv2.bitwise_and(frame, frame, mask=fg_mask)

        return foreground