from typing import List, Optional
import numpy as np
from models.data_frame import DataFrame


class IEffect():
    def apply(self, frame: Optional[np.ndarray], 
              dataframes: List[DataFrame]) -> DataFrame:
        pass