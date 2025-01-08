from typing import List
from models.car_position import CarPosition
from models.parking_space import ParkingSpace
from models.server_response import ServerResponse
from pydantic import BaseModel

class Data(BaseModel):
    id: int
    parking_spaces: List[ParkingSpace]
    car_positions: List[CarPosition]
    server_response: ServerResponse