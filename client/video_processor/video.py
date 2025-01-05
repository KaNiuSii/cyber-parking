import cv2
from typing import Optional
from pathlib import Path
import numpy as np

class Video:
    def __init__(self, video_path: str):
        self.video_path: Path = self.get_file_path(video_path)
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_open: bool = False

    def get_file_path(self, video_name: str) -> Path:
        parent_dir: Path = Path('.').absolute()
        video_dir: Path = parent_dir / 'videos'
        
        video_file_path: Path = video_dir / video_name
        
        return video_file_path

    def open_video(self) -> None:
        self.cap = cv2.VideoCapture(str(self.video_path))  # Convert Path to string for OpenCV
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Cannot open video file: {self.video_path}")
        self.is_open = True

    def close_video(self) -> None:
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.is_open = False

    def get_next_frame(self) -> Optional[np.ndarray]:
        if not self.is_open:
            raise RuntimeError("Video not opened. Call open_video() first.")
        
        ret: bool
        frame: Optional[np.ndarray]
        
        ret, frame = self.cap.read()
        if not ret:
            self.close_video()  # Close the stream if end of video
            return None  # End of video, return None
        
        return frame
