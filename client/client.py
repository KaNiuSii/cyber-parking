import cv2
from video_processor.video_processor import VideoProcessor


def main():
    video_processor = VideoProcessor('cropped.mp4')
    video_processor.process()

main()
