import time
from typing import List
from models.data import Data
from models.car_position import CarPosition
from models.parking_space import ParkingSpace
from workers.iworker import IWorker

class Parked(IWorker):
    def apply(self, data_chain: List[Data], new_data: Data) -> Data:
        relevant_data_chain = data_chain

        maximum: int = max([len(x.parking_spaces) for x in relevant_data_chain])
        now: int = len(new_data.parking_spaces)

        new_data.server_response.parked = min(maximum - now, len(new_data.car_positions))

        return new_data