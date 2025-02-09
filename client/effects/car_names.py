from typing import List, Optional
import cv2
import numpy as np
from effects.ieffect import IEffect
from colors import Colors
from models.data_frame import DataFrame
from models.data import Data, CarPosition
from consts import Consts
from video_processor.data_holder import DataHolder

class CarNames(IEffect):
    ACCEPTED_Y_DIFF = 100
    ACCEPTED_X_DIFF = 100

    def __init__(self):
        self.car_number = 0
        self.lost_cars = []
        self.last_car_positon = []

    def apply(self, frame: Optional[np.ndarray], dataframes: List[DataFrame]) -> DataFrame:
        updated_data = dataframes[-1]

        car_positions_with_names = self.assign_car_names(updated_data.data.car_positions, self.last_car_positon)
        detected_frame_with_positions = self.write_car_positions(frame, car_positions_with_names)

        updated_data.data.car_positions = car_positions_with_names
        self.last_car_positon = car_positions_with_names

        return DataFrame(frame=detected_frame_with_positions, data=updated_data.data)

    def write_car_positions(self, frame: np.ndarray, car_positions: List[CarPosition]):
        for car_position in car_positions:
            cv2.rectangle(frame, (car_position.x - car_position.w // 2, car_position.y - car_position.h // 2),
                          (car_position.x + car_position.w // 2, car_position.y + car_position.h // 2),
                          Colors.PURPLE_BGR, 2)
            # print("Car name:", car_position.name)
            nameString = str(car_position.name)
            cv2.putText(frame, nameString, (car_position.x, car_position.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        Colors.PURPLE_BGR, 2)

        return frame

    def is_same_car(self, car_position: CarPosition, last_car_position: CarPosition) -> bool:
        return abs(car_position.x - last_car_position.x) < self.ACCEPTED_Y_DIFF and abs(
            car_position.y - last_car_position.y) < self.ACCEPTED_X_DIFF

    def assign_car_names(self, car_positions: List[CarPosition], last_car_positions: List[CarPosition]):
        cars_not_found: List[CarPosition] = last_car_positions.copy()

        for car_position in car_positions:
            for last_car_position in cars_not_found:
                if self.is_same_car(car_position, last_car_position):
                    car_position.name = last_car_position.name
                    cars_not_found.remove(last_car_position)
                    break

            if car_position.name == Consts.UNKNOWN:
                for lost_car in self.lost_cars:
                    if self.is_same_car(car_position, lost_car):
                        car_position.name = lost_car.name
                        self.lost_cars.remove(lost_car)
                        break

                if car_position.name == Consts.UNKNOWN:
                    plate = DataHolder.get_next()
                    car_position.name = plate
                    self.car_number += 1

        self.lost_cars.extend(cars_not_found)

        return car_positions
