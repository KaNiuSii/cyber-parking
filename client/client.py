import asyncio
import cv2
from video_processor.video_processor import VideoProcessor
from http_comm.http import Http

async def process_video(file_name: str, flag: int, id: int):
    video_processor = VideoProcessor(file_name, flag, id)
    await asyncio.to_thread(video_processor.process)

async def main():
    id: int = Http.initialize_parking_data()
    
    # video_files = ['goranocrop.mp4', 'filmikzgory.mp4', 'noscroppedwyjazd.mp4']
    video_files = ["http://172.20.10.5:4746/video", "http://172.20.10.6:4747/video", "http://172.20.10.4:4747/video"]
    
    tasks = []
    for i, vf in enumerate(video_files):
        task = asyncio.create_task(process_video(vf, i, id))
        tasks.append(task)
    
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
