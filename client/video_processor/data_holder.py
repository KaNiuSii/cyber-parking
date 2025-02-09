from typing import List
from consts import Consts

entrance_queue: List[str] = []


class DataHolder:
    @staticmethod
    def add(name: str):
        print("Adding to queue:", name)
        entrance_queue.append(name)

    @staticmethod
    def get_next():
        if len(entrance_queue) == 0:
            return Consts.UNKNOWN 
        output = entrance_queue.pop(0)
        print("Returning from queue:", output)
        print("Queue:", entrance_queue)
        return output
    