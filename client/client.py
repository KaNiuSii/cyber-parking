import cv2
from video_processor.video_processor import VideoProcessor
from multiprocessing import Process
from http_comm.http import Http

def process_video(file_name: str, flag: int, id: int):
    video_processor = VideoProcessor(file_name, flag, id)
    video_processor.process()

def main():
    id: int = Http.initialize_parking_data()
    
    # W kolejnosci
    # - wjazd
    # - gora
    # - wyjazd
    video_files = ['wjazd.mp4', 'filmgora.mp4']
    
    processes = []
    i = 0
    for vf in video_files:
        p = Process(target=process_video, args=(vf, i, id))
        processes.append(p)
        p.start()
        i += 1

    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
