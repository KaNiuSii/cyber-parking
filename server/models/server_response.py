from typing import List
from pydantic import BaseModel

class ServerResponse(BaseModel):
    parked: int
    not_moving: List[str]
    parked_names: List[str]