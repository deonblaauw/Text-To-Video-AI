from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.utils import save_video_description_to_file
from utility.script.script_generator import generate_script
from utility.script.hashtag_generator import generate_hashtags
from utility.audio.audio_generator import generate_audio_openai
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
import argparse


if __name__ == "__main__":
    # Argument parsing to include landscape/portrait option and output filename
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")
    parser.add_argument("--landscape", action='store_true', help="Generate video in landscape mode (default is portrait)")
    parser.add_argument("--output_file", type=str, default="video_description.txt", help="The file name to save the script and hashtags")
    parser.add_argument("--duration", type=str, default="10", help="The duration of the video in seconds")

    args = parser.parse_args()
    SAMPLE_TOPIC = args.topic
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"
    PROVIDER = "openai"  # options are: openai | groq
    MODEL = "gpt-4o"     # options are: gpt-4o (for openai) | mixtral-8x7b-32768 (groq)
    VOICE = "Random"     # Options are ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], anything else results in random selection
    OUTPUT_FILE = args.output_file  # File to save the response and hashtags
    VIDEO_DURATION = args.duration
    MUSIC_VOLUME = 0.7   # music volume between 0.0 and 1.0

    # Set landscape orientation based on argument
    LANDSCAPE = args.landscape

    # Print whether landscape or portrait mode is selected
    if LANDSCAPE:
        print("Generating video in landscape mode.")
    else:
        print("Generating video in portrait mode.")

    response = generate_script(SAMPLE_TOPIC, PROVIDER, MODEL , VIDEO_DURATION)
    print("script: {}".format(response))

    vid_hashtags = generate_hashtags(response, PROVIDER, MODEL)
    print("trends: {}".format(vid_hashtags))

    # Save response and hashtags to a file
    save_video_description_to_file(OUTPUT_FILE, response, vid_hashtags)

    # Uses OpenAI's TTS instead of Edge TTS. 
    asyncio.run(generate_audio_openai(response, SAMPLE_FILE_NAME , VOICE))

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    print("[DEBUG] Timed captions coming in hot:")
    print(timed_captions)

    search_terms = getVideoSearchQueriesTimed(response, timed_captions, PROVIDER, MODEL)
    print("[DEBUG] Search terms coming in hot:")
    print(search_terms)

    background_video_urls = None
    if search_terms is not None:
        background_video_urls = generate_video_url(search_terms, VIDEO_SERVER, orientation_landscape=LANDSCAPE)
        print(background_video_urls)
    else:
        print("No background video")

    if background_video_urls is not None:
        background_video_urls = merge_empty_intervals(background_video_urls)
        if background_video_urls is not None:
            video = get_output_media(SAMPLE_TOPIC, SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER, LANDSCAPE , MUSIC_VOLUME)
            print(video)
        else:
            print("No background video after merging intervals")
    else:
        print("No background video")
