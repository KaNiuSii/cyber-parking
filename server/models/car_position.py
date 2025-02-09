from pydantic import BaseModel
from typing import Optional

class CarPosition(BaseModel):
    name: str
    x: int
    y: int
    w: int
    h: int
    is_parked: bool = False                
    parked_spot: Optional[int] = None