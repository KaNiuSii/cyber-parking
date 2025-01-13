from typing import List
import cv2
import numpy as np
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

            dataframe: DataFrame = DataFrame(
                frame=frame,
                data=Data(
                    id=self.data_id,
                    car_positions=[],
                    parking_spaces=[],
                    server_response=ServerResponse(parked=0, not_moving=[], parked_names=[])
                )
            )

            self.dataframes.append(dataframe)
            
            for effect in self.effects:
                dataframe = effect.apply(frame, self.dataframes)
                self.dataframes.append(dataframe)

            update_payload = self.dataframes[-1].data.model_dump()

            response = requests.post(f"{self.api_url}/update_parking_data", json=update_payload)
            server_data = Data.model_validate(response.json()["data"])

            response_frame = self.write_server_response(server_data.server_response)

            cv2.imshow('Main Frame', frame)
            cv2.imshow('Server Response', response_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video.close_video()


    def write_server_response(self, resp: ServerResponse) -> np.ndarray:
        frame_width, frame_height = 400, 300
        response_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

        text_data = resp.model_dump()

        y_offset = 20
        line_height = 20
        margin = 10

        for key, value in text_data.items():
            if isinstance(value, list):
                value_str = " | ".join(map(str, value))
            else:
                value_str = str(value)

            text = f"{key.capitalize()}: {value_str}"

            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            max_text_width = frame_width - 2 * margin
            while text_size[0] > max_text_width:
                split_idx = text[:max_text_width // 7].rfind(' ')
                wrapped_line = text[:split_idx]
                remaining_line = text[split_idx + 1:]

                cv2.putText(
                    response_frame,
                    wrapped_line,
                    (margin, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )
                y_offset += line_height

                text = remaining_line
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]

            cv2.putText(
                response_frame,
                text,
                (margin, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
            y_offset += line_height

            if y_offset > frame_height - line_height:
                break

        return response_frame





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

        server_data = Data.model_validate(response.json()["data"])
        self.data_id = server_data.id

        print(f"Initialized parking data with ID: {self.data_id}")
