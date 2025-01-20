from typing import List
import cv2
import numpy as np
import requests
from effects.car_names import CarNames
from effects.car_positions import CarPositions
from effects.parking_spaces import ParkingSpaces
from video_processor.video import Video
from video_processor.server_response_frame import ServerResponseFrame
from models.data_frame import DataFrame
from models.data import Data
from models.server_response import ServerResponse
from effects.ieffect import IEffect
from http_comm.http import Http
from effects.license_plate_detector import LicensePlateDetector


class VideoProcessor:
    def __init__(self, video_path: str):
        self.video: Video = Video(video_path)
        self.video.open_video()
        self.effects: List[IEffect] = self.register_effects()
        self.dataframes: List[DataFrame] = []
        self.data_id = None

    def process(self):
        self.data_id = Http.initialize_parking_data()
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


            response = Http.update_parking_data(data=self.dataframes[-1].data)

            response_frame = ServerResponseFrame.write_server_response(resp=response.server_response)

            # cv2.imshow('Main Frame', frame)
            # cv2.imshow('Server Response', response_frame)
            #
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        self.video.close_video()

    def register_effects(self) -> List[IEffect]:
        return [
            CarPositions(),
            ParkingSpaces(),
            CarNames(),
            LicensePlateDetector()
        ]
    
    
