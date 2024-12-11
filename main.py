"""
Video Bot
----------
A Python-based bot to download videos, upload them to a platform via API, and auto-delete after upload.

Features:
- Monitors a folder for video files
- Downloads videos from supported platforms
- Uploads videos to specified API endpoints
- Handles async operations for efficiency
- Auto-delete local files after successful upload.

Author: SHUBH YADAV
Date: 2024-12-12
"""



import os
import asyncio
import json
import requests
from aiohttp import ClientSession
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from yt_dlp import YoutubeDL
import shutil
import logging
import time

# Configuration
VIDEO_DIR = './videos'
FAILED_DIR = './failed_videos'
API_BASE_URL = 'https://api.socialverseapp.com'
FLIC_TOKEN = "flic_fa3666fe7b4a1eb7126de29b1bca986b52bb2336e856d97f240cd4f51fd83a89"  # Replace with your actual token

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Download video using yt-dlp
async def download_video(video_url, filename):
    filepath = os.path.join(VIDEO_DIR, filename)
    ydl_opts = {
        'outtmpl': filepath,  # Save file with the given filename
        'format': 'bestvideo+bestaudio/best',  # Best video + audio
        'noplaylist': True,  # Avoid downloading playlists
        'quiet': False,  # Display download progress
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        logging.info(f"Downloaded video: {filename}")
        
        # After downloading, check if the merged file exists and update the filepath
        merged_filepath = os.path.join(VIDEO_DIR, f"{filename}.mp4")
        if os.path.exists(merged_filepath):
            os.rename(merged_filepath, filepath)  # Rename the merged file to the desired filename
            logging.info(f"Merged and renamed video to: {filepath}")
        
    except Exception as e:
        logging.error(f"Error downloading video from {video_url}: {e}")

# Fetch and download videos
async def fetch_and_download_videos():
    # Ask the user for the video URL
    video_urls = []
    while True:
        video_url = input("Enter the video URL (or press Enter to stop adding links): ").strip()
        if not video_url:
            break
        video_urls.append(video_url)

    if not video_urls:
        logging.warning("No video URLs provided. Exiting the download process.")
        return

    # Download each video
    tasks = [download_video(url, f"video_{i}.mp4") for i, url in enumerate(video_urls)]
    await asyncio.gather(*tasks)


# Function to upload video
async def upload_video(upload_url, video_path):
    try:
        with open(video_path, 'rb') as video_file:
            response = requests.put(upload_url, data=video_file)
            response.raise_for_status()
            logging.info(f"Video uploaded successfully to {upload_url} \"{response.status_code} {response.reason}\"")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error uploading video: {e}")
        return False
    return True

# Function to create a post
async def create_post(title, video_hash, category_id):
    try:
        data = {
            "title": title,
            "hash": video_hash,
            "is_available_in_public_feed": False,
            "category_id": category_id
        }
        response = requests.post(
            'https://api.socialverseapp.com/posts',
            headers={
                'Flic-Token': FLIC_TOKEN,
                'Content-Type': 'application/json'
            },
            json=data
        )
        response.raise_for_status()
        logging.info(f"Post created successfully: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating post: {e}")
        return False

# Function to move file to failed directory
class VideoHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop

    def on_created(self, event):
        # Log event for debugging
        logging.debug(f"Event detected: {event.src_path}")
        if event.src_path.endswith('.mp4'):
            logging.debug(f"Video file detected: {event.src_path}")
            # Schedule the task to process video
            time.sleep(2)  # Give time for merging process (increase if needed)
            self.loop.call_soon_threadsafe(asyncio.create_task, self.process_video(event.src_path))

    async def process_video(self, video_path):
        logging.info(f"Started processing video: {video_path}")
        try:
            final_video_path = './videos/video_0.mp4'  # Change to final merged video file

            logging.debug(f"Checking if final video exists at: {final_video_path}")
            if not os.path.exists(final_video_path):
                logging.error(f"File does not exist: {final_video_path}")
                self.move_to_failed(final_video_path)
                return

            logging.info(f"Final video ready: {final_video_path}")

            # Proceed with the video processing logic
            upload_url_data = await self.get_upload_url(final_video_path)
            if not upload_url_data:
                self.move_to_failed(final_video_path)
                return

            # Upload video logic
            upload_url = upload_url_data.get('url')
            if not await upload_video(upload_url, final_video_path):
                self.move_to_failed(final_video_path)
                return

            # Create post after upload
            title = os.path.basename(final_video_path)
            category_id = 1  # Change as necessary
            video_hash = upload_url_data.get('hash')
            if not await create_post(title, video_hash, category_id):
                self.move_to_failed(final_video_path)
                return

        # Successfully processed video; delete the file
            try:
                os.remove(final_video_path)
                logging.info(f"Deleted video after successful processing: {final_video_path}")
            except Exception as e:
                logging.error(f"Error deleting file {final_video_path}: {e}")

            logging.info(f"Video {final_video_path} processed successfully")
        except Exception as e:
            logging.error(f"Error processing video {video_path}: {e}")
            self.move_to_failed(final_video_path)


    def move_to_failed(self, video_path):
        try:
            failed_video_path = os.path.join('./failed_videos', os.path.basename(video_path))
            if not os.path.exists('./failed_videos'):
                os.makedirs('./failed_videos')
            os.rename(video_path, failed_video_path)
            logging.error(f"Moved file to failed directory: {failed_video_path}")
        except Exception as e:
            logging.error(f"Error moving file to failed directory: {e}")

    async def get_upload_url(self, video_path):
        try:
            response = requests.get(
                'https://api.socialverseapp.com/posts/generate-upload-url',
                headers={
                    'Flic-Token': FLIC_TOKEN,
                    'Content-Type': 'application/json'
                }
            )
            response.raise_for_status()
            logging.info(f"HTTP Request: GET {response.url} \"{response.status_code} {response.reason}\"")
            return response.json()  # Return JSON response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting upload URL: {e}")
            return None
        
        
# Main function to start monitoring
async def main():
    loop = asyncio.get_running_loop()
    event_handler = VideoHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, path=VIDEO_DIR, recursive=False)
    observer.start()
    print(f"Monitoring directory: {VIDEO_DIR}")
    
    # Trigger video downloads
    await fetch_and_download_videos()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    asyncio.run(main())
