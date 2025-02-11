# import cv2
# from typing import Optional
# from pathlib import Path
# import numpy as np

# class Video:
#     def __init__(self, video_path: str):
#         self.video_path: Path = self.get_file_path(video_path)
#         self.cap: Optional[cv2.VideoCapture] = None
#         self.is_open: bool = False

#     def get_file_path(self, video_name: str) -> Path:
#         parent_dir: Path = Path('.').absolute()
#         video_dir: Path = parent_dir / 'videos'
        
#         video_file_path: Path = video_dir / video_name
        
#         return video_file_path

#     def open_video(self) -> None:
#         self.cap = cv2.VideoCapture(str(self.video_path))  # Convert Path to string for OpenCV
#         if not self.cap.isOpened():
#             raise FileNotFoundError(f"Cannot open video file: {self.video_path}")
#         self.is_open = True

#     def close_video(self) -> None:
#         if self.cap:
#             self.cap.release()
#         cv2.destroyAllWindows()
#         self.is_open = False

#     def get_next_frame(self) -> Optional[np.ndarray]:
#         if not self.is_open:
#             raise RuntimeError("Video not opened. Call open_video() first.")
        
#         ret: bool
#         frame: Optional[np.ndarray]
        
#         ret, frame = self.cap.read()
#         if not ret:
#             self.close_video()  # Close the stream if end of video
#             return None  # End of video, return None
        
#         return frame


## MAC VERSION




# import cv2
# from typing import Optional
# from pathlib import Path
# import numpy as np

# class Video:
#     def __init__(self, video_path: str):
#         self.video_path: Path = self.get_file_path(video_path)
#         self.cap: Optional[cv2.VideoCapture] = None
#         self.is_open: bool = False

#     def get_file_path(self, video_name: str) -> Path:
#         parent_dir: Path = Path('.').absolute()
#         video_dir: Path = parent_dir / 'videos'
#         video_file_path: Path = video_dir / video_name
#         return video_file_path

#     def open_video(self) -> None:
#         self.cap = cv2.VideoCapture(str(self.video_path))  # Convert Path to string for OpenCV
#         if not self.cap.isOpened():
#             raise FileNotFoundError(f"Cannot open video file: {self.video_path}")
#         self.is_open = True

#     def close_video(self) -> None:
#         if self.cap:
#             self.cap.release()
#         # Do not call cv2.destroyAllWindows() here;
#         # GUI cleanup will be handled in the main display loop.
#         self.is_open = False

#     def get_next_frame(self) -> Optional[np.ndarray]:
#         if not self.is_open:
#             raise RuntimeError("Video not opened. Call open_video() first.")
        
#         ret, frame = self.cap.read()
#         if not ret:
#             self.close_video()  # Close the stream if end of video
#             return None  # End of video, return None
        
#         return frame



import cv2
from typing import Optional
from pathlib import Path
import numpy as np

class Video:
    def __init__(self, source: str):
        """
        Initialize with either a file name (for a local video in ./videos folder)
        or a full URL (for an IP camera stream).
        """
        if source.startswith("http://") or source.startswith("https://") or source.startswith("rtsp://"):
            # Treat source as an IP camera or network stream URL.
            self.video_source: str = source
        else:
            # Treat source as a video file name located in the ./videos directory.
            self.video_source = str(self.get_file_path(source))
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_open: bool = False

    def get_file_path(self, video_name: str) -> Path:
        parent_dir: Path = Path('.').absolute()
        video_dir: Path = parent_dir / 'videos'
        video_file_path: Path = video_dir / video_name
        return video_file_path

    def open_video(self) -> None:
        # Open the video source (file path or IP camera URL)
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Cannot open video source: {self.video_source}")
        self.is_open = True

    def close_video(self) -> None:
        if self.cap:
            self.cap.release()
        self.is_open = False

    def get_next_frame(self) -> Optional[np.ndarray]:
        if not self.is_open:
            raise RuntimeError("Video not opened. Call open_video() first.")
        
        ret, frame = self.cap.read()
        if not ret:
            self.close_video()  # Close the stream if end of video or stream interruption
            return None  # End of video/stream, return None
        
        return frame
