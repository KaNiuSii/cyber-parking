import numpy as np
import cv2
from effects.ieffect import IEffect
from colors import Colors
import pickle


class ParkingSpaceCreate(IEffect):
    def __init__(self):
        self.width, self.height = 50, 68 
        try:
            with open('CarParkPos', 'rb') as f:
                self.posList = pickle.load(f)
        except:
            self.posList = []
        self.paused = False
        self.pause_start_time = None

    def mouseClick(self, events, x : int, y : int, flags, params):
        if events == cv2.EVENT_LBUTTONDOWN:
            self.posList.append((x, y))
        with open('SpacePostions', 'wb') as f:
            pickle.dump(self.posList, f)

    def apply(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return None

        cv2.namedWindow("Frame")

        for pos in self.posList:
            cv2.rectangle(frame, pos, (pos[0] + self.width, pos[1] + self.height), (255, 0, 255), 2)
            cv2.putText(frame, "Parking Spot", (pos[0], pos[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)

        cv2.setMouseCallback("Frame", self.mouseClick)

        return frame