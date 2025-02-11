# import asyncio
# import cv2
# from video_processor.video_processor import VideoProcessor
# from http_comm.http import Http

# async def process_video(file_name: str, flag: int, id: int):
#     video_processor = VideoProcessor(file_name, flag, id)
#     await asyncio.to_thread(video_processor.process)

# async def main():
#     id: int = Http.initialize_parking_data()
    
#     video_files = ['wjazd.mp4', 'gora1.mp4', 'wyjazd.mp4']
    
#     # Create tasks for each video file
#     tasks = []
#     for i, vf in enumerate(video_files):
#         task = asyncio.create_task(process_video(vf, i, id))
#         tasks.append(task)
    
#     # Wait for all tasks to complete
#     await asyncio.gather(*tasks)

# if __name__ == '__main__':
#     asyncio.run(main())

## MAC VERSION




import asyncio
import cv2
import threading
import time
from queue import Queue
from video_processor.video_processor import VideoProcessor
from http_comm.http import Http

# Create a thread-safe queue for frames to be displayed.
display_queue = Queue()

def display_loop():
    """Run on the main thread to display frames coming from the display_queue."""
    while True:
        if not display_queue.empty():
            try:
                # Retrieve the next display items: a tuple (main_frame, response_frame)
                main_frame, response_frame = display_queue.get(timeout=0.1)
                cv2.imshow('Main Frame', main_frame)
                cv2.imshow('Server Response', response_frame)
            except Exception as e:
                # If there's an error (for example, an empty queue), continue.
                pass

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        time.sleep(0.01)
    cv2.destroyAllWindows()

async def process_video(file_name: str, flag: int, id: int):
    # Pass the display_queue to the VideoProcessor so it can send frames for display.
    video_processor = VideoProcessor(file_name, flag, id, display_queue)
    await asyncio.to_thread(video_processor.process)

async def async_main():
    # Initialize parking data on the server.
    id: int = Http.initialize_parking_data()
    
    video_files = ["http://172.20.10.5:4746/video", "http://172.20.10.6:4747/video"]
    
    # Create an async task for each video file.
    tasks = []
    for i, vf in enumerate(video_files):
        task = asyncio.create_task(process_video(vf, i, id))
        tasks.append(task)
    
    # Wait for all video processing tasks to complete.
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Run the asyncio video processing in a separate thread
    # so that the main thread can run the display loop.
    loop_thread = threading.Thread(target=lambda: asyncio.run(async_main()))
    loop_thread.start()
    
    # Run the display loop in the main thread.
    display_loop()
    
    loop_thread.join()
