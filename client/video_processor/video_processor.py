from typing import List
import cv2
import effects.background_removal
import effects.color_filter
import effects.car_positions
import effects.ieffect
import effects.parking_spaces
from video_processor.video import Video
import effects

class VideoProcessor:
    def __init__(self, video_path: str):
        self.video = Video(video_path)
        self.video.open_video()
        self.effects = self.register_effects()

    def process(self):
        while True:
            frame = self.video.get_next_frame()
            if frame is None:
                break
            for effect in self.effects:
                frame = effect.apply(frame)
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video.close_video()

    def register_effects(self) -> List[effects.ieffect.IEffect]:
        return [
                effects.color_filter.ColorFilter(),
                effects.car_positions.CarPositions(),
                effects.parking_spaces.ParkingSpaces()
            ]
