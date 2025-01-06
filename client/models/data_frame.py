from typing import Optional
import numpy as np
from models.data import Data

class DataFrame:
    def __init__(self, frame: Optional[np.ndarray], data: Data):
        self.frame = frame
        self.data = data