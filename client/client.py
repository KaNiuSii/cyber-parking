import cv2
from video_processor.video import Video



def main():
    video_processor = Video('1.mp4')
    video_processor.open_video()

    while True:
        frame = video_processor.get_next_frame()
        if frame is None:
            break
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_processor.close_video()

main()