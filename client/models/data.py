from typing import List
from models.car_position import CarPosition
from models.parking_space import ParkingSpace

class Data:
    def __init__(
            self, parking_spaces: List[ParkingSpace], 
            car_positions: List[CarPosition]
            ):
        self.parking_spaces = parking_spaces
        self.car_positions = car_positions
        
