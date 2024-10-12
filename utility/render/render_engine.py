import time
import os
import tempfile
import zipfile
import platform
import subprocess
import PIL
import random
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

def download_file(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url)
        f.write(response.content)

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

import os
import random
from moviepy.editor import AudioFileClip, vfx

def get_music():
    # Define the path to the background_music folder
    music_folder = "background_music"

    # List all .wav files in the folder
    music_files = [f for f in os.listdir(music_folder) if f.endswith('.wav')]

    # Select a random .wav file from the list
    if music_files:
        music_file_path = os.path.join(music_folder, random.choice(music_files))
    else:
        music_file_path = None  # If no music files found, return None
    
    return music_file_path

def get_output_media(sample_topic, audio_file_path, timed_captions, background_video_data, video_server, landscape):
    
    if len(sample_topic) < 40:
        OUTPUT_FILE_NAME = sample_topic.replace(" ", "_") + ".mp4"
    else:
        OUTPUT_FILE_NAME = "rendered_video.mp4"

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
            print("No resize needed")
        
        visual_clips.append(video_clip)

    
    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)

    for (t1, t2), text in timed_captions:
        text_clip = TextClip(txt=text, fontsize=100, color="white", stroke_width=3, stroke_color="black", method="label")
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
        music_clip = music_clip.volumex(0.80)

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
