from typing import List
from pydantic import BaseModel

class ServerResponse(BaseModel):
    parked: int
