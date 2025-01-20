import requests

from models.data import Data

from consts import Consts


class Http:

    @staticmethod
    def initialize_parking_data() -> int:
        initial_data = {
            "parking_spaces": [],
            "car_positions": [],
            "license_plates": []
        }

        response = requests.post(
            f"{Consts.API_URL}/create_parking_data",
            json=initial_data
        )

        server_data = Data.model_validate(response.json()["data"])
        return server_data.id

    @staticmethod
    def update_parking_data(data: Data) -> Data:
        update_payload = data.model_dump(mode='json')
        response = requests.post(f"{Consts.API_URL}/update_parking_data", json=update_payload)
        return Data.model_validate(response.json()["data"])

    