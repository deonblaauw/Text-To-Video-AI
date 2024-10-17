import time
import os
import tempfile
import zipfile
import platform
import subprocess
import PIL
import random
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip, vfx)
# from moviepy.audio.fx.audio_loop import audio_loop
# from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

# def download_file(url, filename):
#     with open(filename, 'wb') as f:
#         response = requests.get(url)
#         f.write(response.content)

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# import requests

def download_file(url, output_path):
    retry_strategy = Retry(
        total=5,  # Number of retry attempts
        backoff_factor=1,  # Time to wait between retries
        status_forcelist=[429, 500, 502, 503, 504],  # List of status codes to retry on
        allowed_methods=["GET"],  # Use 'allowed_methods' instead of 'method_whitelist'
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, stream=True)
        response.raise_for_status()

        # Write the file in chunks to avoid memory issues
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
        print(f"Downloaded file saved to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")




def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_music():
    # Define the path to the background_music folder
    music_folder = "background_music"

    # List all .wav files in the folder
    music_files = [f for f in os.listdir(music_folder) if f.endswith('.wav') or f.endswith('.mp3') ]

    # Select a random .wav file from the list
    if music_files:
        music_file_path = os.path.join(music_folder, random.choice(music_files))
    else:
        music_file_path = None  # If no music files found, return None
    
    return music_file_path

def get_output_media(sample_topic, audio_file_path, timed_captions, background_video_data, video_server, landscape, volume_wav,volume_mp3, volume_tts , output_directory):

    # Create the directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Limit the filename to 40 characters and replace spaces with underscores
    filename_base = sample_topic.replace(" ", "_")[:40]

    # Set the initial output file name
    OUTPUT_FILE_NAME = os.path.join(output_directory, filename_base + ".mp4")

    # Check if the file already exists, and append a number if necessary
    counter = 1
    while os.path.exists(OUTPUT_FILE_NAME):
        # If the file exists, append a counter to the filename before the extension
        OUTPUT_FILE_NAME = os.path.join(output_directory, f"{filename_base}_{counter}.mp4")
        counter += 1

    magick_path = get_program_path("magick")
    print(magick_path)
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    visual_clips = []

    for (t1, t2), video_url in background_video_data:
        # Download the video file
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        
        # Create VideoFileClip from the downloaded file
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.set_start(t1)
        video_clip = video_clip.set_end(t2)
        
        # Check the orientation and target size
        if landscape:
            target_size = (1920, 1080)
        else:
            target_size = (1080, 1920)
        
        # Only resize if the video size does not match the target size
        if video_clip.size != list(target_size):
            print("Incorrect Clip size detected: ", video_clip.size)
            print("Resizing clip to: ", target_size)
            video_clip = video_clip.resize(target_size, PIL.Image.Resampling.LANCZOS)
        else:
            print("Clip processed")
        
        visual_clips.append(video_clip)

    audio_clips = []

    # Add the generated TTS audio to the video
    if audio_file_path:
        audio_file_clip = AudioFileClip(audio_file_path)
        # Ensure TTS is at max volume
        audio_file_clip = audio_file_clip.volumex(volume_tts)
        audio_clips.append(audio_file_clip)

    for (t1, t2), text in timed_captions:
        text_clip = TextClip(txt=text, fontsize=150, transparent=True, bg_color = "transparent", font = "Lane" , color="white", stroke_width=3, stroke_color="black", method="label")
        text_clip = text_clip.set_start(t1)
        text_clip = text_clip.set_end(t2)
        text_clip = text_clip.set_position(["center", 800])
        visual_clips.append(text_clip)

    # Get music
    music_file_path = get_music()
    
    # Add the generated music to the video
    if music_file_path:
        music_clip = AudioFileClip(music_file_path)
        
        # Adjust volume (e.g., reduce to 80%)
        if music_file_path.endswith('.wav'):
            music_clip = music_clip.volumex(volume_wav)
        elif music_file_path.endswith('.mp3'):
            music_clip = music_clip.volumex(volume_mp3)
        else:
            print("Unsupported file format: " , music_file_path.encode)
        

        # Loop the music to fit the video duration
        video_duration = sum([(t2 - t1) for (t1, t2), _ in background_video_data])
        music_clip = music_clip.fx(vfx.loop, duration=video_duration)
        
        audio_clips.append(music_clip)

    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')
    
    # Clean up downloaded files
    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        os.remove(video_filename)

    return OUTPUT_FILE_NAME


