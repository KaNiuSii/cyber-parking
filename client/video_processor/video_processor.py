from typing import List
import cv2
import effects.color_filter
import effects.car_positions
import effects.ieffect
import effects.parking_spaces
from video_processor.video import Video
from effects.ieffect import IEffect 
from models.data_frame import DataFrame

class VideoProcessor:
    def __init__(self, video_path: str):
        self.video: Video = Video(video_path)
        self.video.open_video()
        self.effects: List[IEffect] = self.register_effects()
        self.dataframes: List[DataFrame] = []

    def process(self):
        while True:
            frame = self.video.get_next_frame()
            if frame is None:
                break
            dataframe: DataFrame
            for effect in self.effects:
                dataframe = effect.apply(frame, self.dataframes)
            self.dataframes.append(dataframe)
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video.close_video()

    def register_effects(self) -> List[IEffect]:
        return [
                # effects.color_filter.ColorFilter(),
                effects.car_positions.CarPositions(),
                effects.parking_spaces.ParkingSpaces()
            ]
