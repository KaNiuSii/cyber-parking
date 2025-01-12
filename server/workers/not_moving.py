import math
import time
from typing import List
from models.data import Data
from models.car_position import CarPosition
from models.parking_space import ParkingSpace
from workers.iworker import IWorker

DIFF: int = 10
FRAMES_WHEN_SEEN: int = 10

class NotMoving(IWorker):
    def apply(self, data_chain: List[Data], new_data: Data) -> Data:
        if len(data_chain) < FRAMES_WHEN_SEEN:
            return new_data
        
        relevant_data_chain = data_chain[-FRAMES_WHEN_SEEN:]
        
        not_moving_names: List[str] = []

        for current_car in new_data.car_positions:
            last_positions: List[CarPosition] = self.last_positions_of_a_car(relevant_data_chain, current_car.name)
            
            if len(last_positions) < FRAMES_WHEN_SEEN:
                continue
                
            
            X: List[int] = [p.x for p in last_positions]
            min_x: int = min(X)
            max_x: int = max(X)

            Y: List[int] = [p.y for p in last_positions]
            min_y: int = min(Y)
            max_y: int = max(Y)

            if abs(max_x - min_x) < DIFF and abs(max_y - min_y) < DIFF:
                not_moving_names.append(current_car.name)

        new_data.server_response.not_moving = not_moving_names

        return new_data
    
    def last_positions_of_a_car(self, data_chain: List[Data], name: str) -> List[CarPosition]:
        last_positions: List[CarPosition] = []
        for data in data_chain:
            for cp in data.car_positions:
                if cp.name == name:
                    last_positions.append(cp)
        return last_positions