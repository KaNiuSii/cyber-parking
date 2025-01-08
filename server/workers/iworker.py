from typing import List
from models.data import Data

class IWorker():
    def apply(self, data_chain: List[Data], new_data: Data) -> Data:
        pass