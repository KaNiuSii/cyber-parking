from typing import List
from consts import Consts
from models.license_plate import LicensePlate

entrance_queue: List[LicensePlate] = []
exit_queue: List[LicensePlate] = []


class DataHolder:
    @staticmethod
    def add(license: LicensePlate):
        print("Adding to queue:", license.number)
        entrance_queue.append(license)

    @staticmethod
    def get_next():
        if len(entrance_queue) == 0:
            return LicensePlate(number=Consts.UNKNOWN, arrival_time=0)
        output = entrance_queue.pop(0)
        print("Returning from queue:", output.number)
        print("Queue:", entrance_queue)
        return output
    
    @staticmethod
    def clear():
        entrance_queue.clear()
        print("Queue cleared")
        
    @staticmethod
    def add_exit(license: LicensePlate):
        print("Adding to exit queue:", license.number)
        exit_queue.append(license)
    