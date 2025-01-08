from typing import Optional
import numpy as np
from models.data import Data
from pydantic import BaseModel

class DataFrame(BaseModel):
    frame: Optional[np.ndarray]
    data: Data

    class Config:
        arbitrary_types_allowed = True