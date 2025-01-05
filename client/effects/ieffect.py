from typing import Optional
import numpy as np


class IEffect():
    def apply(frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        pass