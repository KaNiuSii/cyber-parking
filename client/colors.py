import numpy as np

class Colors:
    # Yellow color range in HSV
    YELLOW_LOWER = np.array([10, 50, 50])
    YELLOW_UPPER = np.array([80, 255, 255])

    # Red color range in HSV (two ranges to account for both low and high red)
    RED_LOWER1 = np.array([0, 120, 70])
    RED_UPPER1 = np.array([10, 255, 255])
    RED_LOWER2 = np.array([170, 120, 70])
    RED_UPPER2 = np.array([180, 255, 255])

    # BGR colors for yellow and red
    YELLOW_BGR = (0, 255, 255)  # Yellow in BGR format
    RED_BGR = (0, 0, 255)  # Red in BGR format
