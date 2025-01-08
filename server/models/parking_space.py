from pydantic import BaseModel

class ParkingSpace(BaseModel):
    id: int
    x: int
    y: int
    w: int
    h: int