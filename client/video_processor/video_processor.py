import asyncio
from typing import List
import cv2
import numpy as np
import requests
from effects.car_names import CarNames
from effects.car_positions import CarPositions
from effects.parking_spaces import ParkingSpaces
from effects.license_detection import LicenseDetector
from effects.license_detection import operatingMode
from video_processor.video import Video
from video_processor.server_response_frame import ServerResponseFrame
from models.data_frame import DataFrame
from models.data import Data
from models.server_response import ServerResponse
from effects.ieffect import IEffect
from http_comm.http import Http


class VideoProcessor:
    def __init__(self, video_path: str, flag: int, id: int):
        self.video: Video = Video(video_path)
        self.video.open_video()
        self.flag = flag #flag
        self.effects: List[IEffect] = self.register_effects()
        self.dataframes: List[DataFrame] = []
        self.data_id = id

    async def process(self):
        if self.flag==1:
            await asyncio.sleep( 5 )
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
                    enterance_license_plates=[],
                    exit_license_plates=[],
                    server_response=ServerResponse(parked=0, not_moving=[], parked_names=[], enterence_license_plates=[], exit_license_plates=[])
                )
            )

            self.dataframes.append(dataframe)
            
            for effect in self.effects:
                dataframe = effect.apply(frame, self.dataframes)
                self.dataframes.append(dataframe)

            if self.flag == 1:
                response = await Http.update_parking_data(data=self.dataframes[-1].data)
                response_frame = ServerResponseFrame.write_server_response(resp=response.server_response)

                cv2.imshow('Main Frame', frame)
                cv2.imshow('Server Response', response_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video.close_video()

    def register_effects(self) -> List[IEffect]:
        if self.flag == 1:
            return [CarPositions(), ParkingSpaces(), CarNames()]
        elif self.flag == 0:
            return [LicenseDetector(operatingMode.enterance)]
        else:
            return [LicenseDetector(operatingMode.exit)]
    
    
