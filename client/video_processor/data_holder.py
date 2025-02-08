from typing import List
from consts import Consts

entrance_queue: List[str] = []


class DataHolder:
    @staticmethod
    def add(name: str):
        entrance_queue.append(name)

    @staticmethod
    def get_next():
        if len(entrance_queue) == 0:
            return Consts.UNKNOWN 
        return entrance_queue.pop(0)
    