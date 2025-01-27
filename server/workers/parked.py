# import time
# from typing import List
# from models.data import Data
# from models.car_position import CarPosition
# from models.parking_space import ParkingSpace
# from workers.iworker import IWorker

# class Parked(IWorker):
#     def apply(self, data_chain: List[Data], new_data: Data) -> Data:
#         relevant_data_chain = data_chain

#         maximum: int = max([len(x.parking_spaces) for x in relevant_data_chain])
#         now: int = len(new_data.parking_spaces)

#         new_data.server_response.parked = min(maximum - now, len(new_data.car_positions))

#         return new_data
# workers/parked.py

from typing import List
import datetime

from workers.iworker import IWorker
from models.data import Data, CarPosition
from models.parking_space import ParkingSpace
from logic.database import insert_parking_event, update_parking_event_end_time

class Parked(IWorker):

    def __init__(self):
        self.active_events = {}

    def apply(self, data_chain: List[Data], new_data: Data) -> Data:
        current_cars_on_spots = self.detect_cars_on_spots(new_data.parking_spaces, new_data.car_positions)
        prev_data = data_chain[-1] if data_chain else None
        previous_cars_on_spots = set()
        if prev_data:
            previous_cars_on_spots = self.detect_cars_on_spots(prev_data.parking_spaces, prev_data.car_positions)

        newly_parked = current_cars_on_spots - previous_cars_on_spots
        unparked = previous_cars_on_spots - current_cars_on_spots

        for (car_id, spot_id) in newly_parked:
            event_id = insert_parking_event(
                car_id=car_id,
                spot_id=spot_id,
                # start_time=datetime.datetime.now().isoformat(timespec='seconds')
                start_time = None
            )
            self.active_events[(car_id, spot_id)] = event_id

        for (car_id, spot_id) in unparked:
            event_id = self.active_events.get((car_id, spot_id))
            if event_id is not None:
                update_parking_event_end_time(
                    event_id=event_id,
                    end_time=datetime.datetime.now().isoformat(timespec='seconds')
                )
                del self.active_events[(car_id, spot_id)]

        return new_data

    def detect_cars_on_spots(self, parking_spaces: List[ParkingSpace], car_positions: List[CarPosition]):
        """
        Sprawdza, które (car_id, spot_id) pary nakładają się w obrazie.
        W super uproszczeniu – jeśli bounding box auta "wpada" w bounding box miejsca parkingowego.
        """
        pairs = set()
        for space in parking_spaces:
            sx1, sy1 = space.x - space.w//2, space.y - space.h//2
            sx2, sy2 = space.x + space.w//2, space.y + space.h//2

            for car in car_positions:
                cx1, cy1 = car.x - car.w//2, car.y - car.h//2
                cx2, cy2 = car.x + car.w//2, car.y + car.h//2
                if not (cx2 < sx1 or sx2 < cx1 or cy2 < sy1 or sy2 < cy1):
                    pairs.add((car.name, space.id))
        return pairs