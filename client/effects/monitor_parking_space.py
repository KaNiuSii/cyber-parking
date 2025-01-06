import cv2
import numpy as np
import pickle
from effects.ieffect import IEffect
import cvzone

class ParkingSpaceChecker(IEffect):
    def __init__(self):
        self.width, self.height = 50, 68  
        try:
            with open('SpacePostions', 'rb') as f:
                self.posList = pickle.load(f)
        except:
            self.posList = []

    def checkParkingSpace(self, imgPro, frame):
        spaceCounter = 0

        for pos in self.posList:
            x, y = pos

            imgCrop = imgPro[y:y + self.height, x:x + self.width]
            count = cv2.countNonZero(imgCrop)

            if count < 800: 
                color = (0, 255, 0)
                thickness = 5
                spaceCounter += 1
            else:
                color = (0, 0, 255)
                thickness = 2

            cv2.rectangle(frame, pos, (pos[0] + self.width, pos[1] + self.height), color, thickness)
            cvzone.putTextRect(frame, str(count), (x, y + self.height - 3), scale=1,
                               thickness=2, offset=0, colorR=color)

        cvzone.putTextRect(frame, f'Free: {spaceCounter}/{len(self.posList)}', (100, 50), scale=2,
                           thickness=2, offset=20, colorR=(0, 200, 0))

    def apply(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return None

        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)


        cv2.imshow("imgthre",imgThreshold)

        self.checkParkingSpace(imgDilate, frame)

        return frame
