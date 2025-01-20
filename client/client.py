import cv2
from video_processor.video_processor import VideoProcessor


def main():
    video_processor = VideoProcessor('tablice main.mov')
    video_processor.process()

main()
