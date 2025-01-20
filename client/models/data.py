from datetime import datetime
from typing import List
from pydantic import BaseModel
from models.car_position import CarPosition
from models.parking_space import ParkingSpace
from models.server_response import ServerResponse
from models.license_plate import LicensePlate

class Data(BaseModel):
    id: int
    parking_spaces: List[ParkingSpace]
    car_positions: List[CarPosition]
    server_response: ServerResponse
    license_plates: List[LicensePlate] = []

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }