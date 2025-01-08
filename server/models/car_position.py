from pydantic import BaseModel

class CarPosition(BaseModel):
    name: str
    x: int
    y: int
    w: int
    h: int