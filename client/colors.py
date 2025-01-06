import numpy as np

class Colors:
    # Yellow color range in HSV
    YELLOW_LOWER = np.array([20, 100, 100])
    YELLOW_UPPER = np.array([30, 255, 255])

    # Red color range in HSV
    RED_LOWER1 = np.array([0,   150,  100])
    RED_UPPER1 = np.array([10,  255,  255])
    RED_LOWER2 = np.array([170, 150,  100])
    RED_UPPER2 = np.array([180, 255,  255])

    # Green color range in HSV
    GREEN_LOWER = np.array([35, 100, 100])
    GREEN_UPPER = np.array([85, 255, 255])

    # BGR colors
    #             B     G     R
    YELLOW_BGR = (0,   255,  255)
    RED_BGR    = (0,   0,    255)
    PURPLE_BGR = (145, 45,   92)
    GREEN_BGR =  (0,   255,  0)
    BLACK_BGR =  (0,   0,  0)