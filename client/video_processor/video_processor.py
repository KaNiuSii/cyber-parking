from typing import List
import cv2
import requests
from effects.car_names import CarNames
from effects.car_positions import CarPositions
from effects.parking_spaces import ParkingSpaces
from video_processor.video import Video
from models.data_frame import DataFrame
from models.data import Data
from models.server_response import ServerResponse
from effects.ieffect import IEffect

class VideoProcessor:
    def __init__(self, video_path: str):
        self.video: Video = Video(video_path)
        self.video.open_video()
        self.effects: List[IEffect] = self.register_effects()
        self.dataframes: List[DataFrame] = []
        self.data_id = None
        self.api_url = 'http://127.0.0.1:8000'

    def process(self):
        self.initialize_parking_data()
        while True:
            frame = self.video.get_next_frame()
            if frame is None:
                break
            dataframe: DataFrame = DataFrame(frame=frame, data=Data(car_positions=[], parking_spaces=[], id=self.data_id, server_response=ServerResponse(parked=0)))
            self.dataframes.append(dataframe)
            for effect in self.effects:
                dataframe = effect.apply(frame, self.dataframes)
                self.dataframes.append(dataframe)

            update_payload = {
                "id": self.data_id,
                "parking_spaces": [
                    {"id": ps.id, "x": ps.x, "y": ps.y, "h": ps.h, "w": ps.w} for ps in dataframe.data.parking_spaces
                ],
                "car_positions": [
                    {"name": cp.name, "x": cp.x, "y": cp.y, "h": cp.h, "w": cp.w} for cp in dataframe.data.car_positions
                ],
                "server_response": {"parked": 0}
            }

            response = requests.post(f"{self.api_url}/update_parking_data", json=update_payload)
            server_data = response.json().get("data")

            cv2.putText(
                frame,
                f"Parked Cars: {server_data['server_response']['parked']}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video.close_video()

    def register_effects(self) -> List[IEffect]:
        return [
            CarPositions(),
            ParkingSpaces(),
            CarNames()
        ]
    
    def initialize_parking_data(self):
        initial_data = {
            "parking_spaces": [],
            "car_positions": []
        }
        response = requests.post(
            f"{self.api_url}/create_parking_data",
            json=initial_data
        )
        response_data = response.json()
        self.data_id = response_data["data"]["id"]
        print(f"Initialized parking data with ID: {self.data_id}")
