import asyncio
import cv2
from video_processor.video_processor import VideoProcessor
from http_comm.http import Http

async def process_video(file_name: str, flag: int, id: int):
    video_processor = VideoProcessor(file_name, flag, id)
    await asyncio.to_thread(video_processor.process)

async def main():
    id: int = Http.initialize_parking_data()
    
    video_files = ['goranocrop.mp4', 'filmikzgory.mp4', 'noscroppedwyjazd.mp4']
    
    # Create tasks for each video file
    tasks = []
    for i, vf in enumerate(video_files):
        task = asyncio.create_task(process_video(vf, i, id))
        tasks.append(task)
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())