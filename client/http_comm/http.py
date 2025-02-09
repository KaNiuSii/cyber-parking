import requests
from datetime import datetime
import json
from models.data import Data
from consts import Consts

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class Http:
    @staticmethod
    def initialize_parking_data() -> int:
        initial_data = {
            "parking_spaces": [],
            "car_positions": [],
            "enterance_license_plates": [],
            "exit_license_plates": [],
        }

        response = requests.post(
            f"{Consts.API_URL}/create_parking_data",
            json=initial_data
        )

        server_data = Data.model_validate(response.json()["data"])
        print(f"Initialized parking data with ID: {server_data.id}")
        
        return server_data.id
    
    @staticmethod
    async def update_parking_data(data: Data) -> Data:
        # Convert to dict and use custom encoder
        update_payload = data.model_dump()
        json_payload = json.dumps(update_payload, cls=DateTimeEncoder)
        
        response = requests.post(
            f"{Consts.API_URL}/update_parking_data", 
            data=json_payload,
            headers={'Content-Type': 'application/json'}
        )

        return Data.model_validate(response.json()["data"])