import math
from typing import List
from models.data import Data
from models.car_position import CarPosition
from models.parking_space import ParkingSpace
from workers.iworker import IWorker

SPACE_DIFF: int = 10
CAR_DIFF: int = 50

class ParkedNames(IWorker):
    def __init__(self):
        super().__init__()

    def apply(self, data_chain: List[Data], new_data: Data) -> Data:
        if len(data_chain) <= 5:
            return new_data

        parking_spaces: List[ParkingSpace] = self.average_parking_spaces_positions(data_chain=data_chain)

        cars: List[CarPosition] = new_data.car_positions
        not_moving: List[str] = new_data.server_response.not_moving if hasattr(new_data.server_response, 'not_moving') else []

        new_data.server_response.parked_names = self.parked_names(parking_spaces=parking_spaces, cars=cars, not_moving=not_moving)

        return new_data

    def parked_names(self, parking_spaces: List[ParkingSpace], cars: List[CarPosition], not_moving: List[str]) -> List[str]:
        names: List[str] = []
        for cr in cars:
            for ps in parking_spaces:
                if self.distance(ps.x, ps.y, cr.x, cr.y) <= CAR_DIFF and cr.name in not_moving:
                    names.append(cr.name)
        return names

    def average_parking_spaces_positions(self, data_chain: List[Data]) -> List[ParkingSpace]:
        if not data_chain:
            return []

        average_spaces: List[ParkingSpace] = []

        previous_frame_spaces = data_chain[5].parking_spaces

        if not previous_frame_spaces:
            return []


        for space in previous_frame_spaces:
            avg_x = space.x
            avg_y = space.y
            count = 1

            for data in data_chain[-5:]:
                closest_space = self.find_closest_parking_space(space, data.parking_spaces)

                if closest_space:
                    distance = self.distance(space.x, space.y, closest_space.x, closest_space.y)

                    if distance <= SPACE_DIFF:
                        avg_x += closest_space.x
                        avg_y += closest_space.y
                        count += 1

            average_spaces.append(
                ParkingSpace(
                    id=space.id,            # Retain the original id
                    x=int(avg_x / count),   # Average x position
                    y=int(avg_y / count),   # Average y position
                    w=space.w,              # Retain the original width
                    h=space.h               # Retain the original height
                )
            )

        return average_spaces



    def find_closest_parking_space(self, target_space: ParkingSpace, spaces: List[ParkingSpace]) -> ParkingSpace:
        closest_space = None
        min_distance = float('inf')

        for space in spaces:
            dist = self.distance(target_space.x, target_space.y, space.x, space.y)
            if dist < min_distance:
                closest_space = space
                min_distance = dist

        return closest_space

    @staticmethod
    def distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
