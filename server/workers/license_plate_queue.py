import math
import time
from typing import List
from models.data import Data
from models.license_plate import LicensePlate
from workers.iworker import IWorker

class LicensePlateQueue(IWorker):
    def apply(self, data_chain: List[Data], new_data: Data) -> Data:
        new_data.server_response.enterence_license_plates = data_chain[-1].server_response.enterence_license_plates
        new_data.server_response.exit_license_plates = data_chain[-1].server_response.exit_license_plates
        
        for license_plate in new_data.enterance_license_plates:
            new_data.server_response.enterence_license_plates.append(license_plate.number)
        for license_plate in new_data.exit_license_plates:
            new_data.server_response.exit_license_plates.append(license_plate.number)
            
        return new_data