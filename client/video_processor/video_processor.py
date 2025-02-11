import asyncio
import time
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
from video_processor.data_holder import DataHolder


class VideoProcessor:
    def __init__(self, video_path: str, flag: int, id: int):
        self.video: Video = Video(video_path)
        self.video.open_video()
        self.flag = flag
        self.effects: List[IEffect] = self.register_effects()
        self.dataframes: List[DataFrame] = []
        self.data_id = id

    def process(self):
        # if self.flag == 1:
        #     print('waiting')
        #     time.sleep(40)
        #     print('going')
        while True:
            frame = self.video.get_next_frame()
            if frame is None:
                break
            
            if self.flag == 1:
                # trim image(480, 640, 3) 0% fromt the left, 50% from the right
                frame = frame[:, int(frame.shape[1] * 0):int(frame.shape[1] * 0.5)]
                # trime image(480, 640, 3) 10% from the top, 10% from the bottom
                frame = frame[int(frame.shape[0] * 0.1):int(frame.shape[0] * 0.9), :]
            else:
                # trim image(480, 640, 3) 5% from the top
                frame = frame[int(frame.shape[0] * 0.05):, :]

                

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
                if len(self.dataframes) > 50:
                    self.dataframes.pop(0)

            if self.flag == 1:
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    DataHolder.clear()
                
                response = Http.update_parking_data(data=self.dataframes[-1].data)
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
    
    
## MAC VERSION






# import time
# from typing import List
# import cv2
# import requests
# from effects.car_names import CarNames
# from effects.car_positions import CarPositions
# from effects.parking_spaces import ParkingSpaces
# from effects.license_detection import LicenseDetector, operatingMode
# from video_processor.video import Video
# from video_processor.server_response_frame import ServerResponseFrame
# from models.data_frame import DataFrame
# from models.data import Data
# from models.server_response import ServerResponse
# from effects.ieffect import IEffect
# from http_comm.http import Http
# from video_processor.data_holder import DataHolder

# class VideoProcessor:
#     def __init__(self, video_path: str, flag: int, id: int, display_queue):
#         self.video: Video = Video(video_path)
#         self.video.open_video()
#         self.flag = flag
#         self.effects: List[IEffect] = self.register_effects()
#         self.dataframes: List[DataFrame] = []
#         self.data_id = id
#         self.display_queue = display_queue

#     def process(self):
#         while True:
#             frame = self.video.get_next_frame()
#             if frame is None:
#                 break

#             # Create a new DataFrame instance for this frame.
#             dataframe: DataFrame = DataFrame(
#                 frame=frame,
#                 data=Data(
#                     id=self.data_id,
#                     car_positions=[],
#                     parking_spaces=[],
#                     enterance_license_plates=[],
#                     exit_license_plates=[],
#                     server_response=ServerResponse(
#                         parked=0, 
#                         not_moving=[], 
#                         parked_names=[], 
#                         enterence_license_plates=[], 
#                         exit_license_plates=[]
#                     )
#                 )
#             )

#             self.dataframes.append(dataframe)
            
#             # Apply each effect to the frame.
#             for effect in self.effects:
#                 dataframe = effect.apply(frame, self.dataframes)
#                 self.dataframes.append(dataframe)

#             if self.flag == 1:
#                 # Update parking data on the server.
#                 response = Http.update_parking_data(data=self.dataframes[-1].data)
#                 response_frame = ServerResponseFrame.write_server_response(resp=response.server_response)
                
#                 # Instead of calling cv2.imshow, send the frames to the display queue.
#                 self.display_queue.put((frame, response_frame))

#             # Do not call cv2.waitKey here.
#         self.video.close_video()

#     def register_effects(self) -> List[IEffect]:
#         if self.flag == 1:
#             return [CarPositions(), ParkingSpaces(), CarNames()]
#         elif self.flag == 0:
#             return [LicenseDetector(operatingMode.enterance)]
#         else:
#             return [LicenseDetector(operatingMode.exit)]
