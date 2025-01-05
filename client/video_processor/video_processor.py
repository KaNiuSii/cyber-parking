import cv2
from typing import List
from pathlib import Path

class VideoProcessor:
    def __init__(self, video_path: str):
        self.video_path = self.get_file_path(video_path)
        self.cap = None
        self.is_open = False

    def get_file_path(self, video_name: str):
        parent_dir = Path('.').absolute()
        video_dir = parent_dir / 'videos'
        
        video_file_path = video_dir / video_name
        
        return video_file_path

    def open_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Cannot open video file: {self.video_path}")
        self.is_open = True

    def close_video(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.is_open = False

    def get_next_frame(self):
        if not self.is_open:
            raise RuntimeError("Video not opened. Call open_video() first.")
        
        ret, frame = self.cap.read()
        if not ret:
            self.close_video()  # Close the stream if end of video
            return None  # End of video, return None
        
        return frame

