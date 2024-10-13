from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.utils import save_video_description_to_file
from utility.script.script_generator import generate_script, generate_new_topic
from utility.script.hashtag_generator import generate_hashtags
from utility.audio.audio_generator import generate_audio_openai, generate_audio_edge
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
    parser.add_argument("--tts", type=str, default="openai", help="Text to speech engine. Options are openai or edge. Default is openai")
    parser.add_argument("--output_dir", type=str, default="generated_outputs", help="Foldername where videos and other outputs are stored. Default is generated_outputs")
    parser.add_argument("--duration", type=str, default="50", help="The duration of the video in seconds. Default is 50 seconds")
    parser.add_argument("--num_vids", type=int, default=1, help="Number of videos to generate. Default is 1.")

    args = parser.parse_args()
    SAMPLE_TOPIC = args.topic
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"
    PROVIDER = "openai"
    MODEL = "gpt-4o"
    VOICE = "Random"
    TTS_ENGINE = args.tts
    VIDEO_DURATION = args.duration
    MUSIC_VOLUME = 0.5
    OUTPUTDIR = args.output_dir
    NUM_VIDS = args.num_vids
    LANDSCAPE = args.landscape

    def generate_video(topic):
        # Main video generation process
        response = generate_script(topic, PROVIDER, MODEL, VIDEO_DURATION)
        print("script: {}".format(response))

        vid_hashtags = generate_hashtags(response, PROVIDER, MODEL)
        print("trends: {}".format(vid_hashtags))

        # Save response and hashtags to a file
        save_video_description_to_file(topic, response, vid_hashtags, OUTPUTDIR)

        if TTS_ENGINE == "openai":
            asyncio.run(generate_audio_openai(response, SAMPLE_FILE_NAME, VOICE))
            print("TTS ENGINE: Openai-tts")
        elif TTS_ENGINE == "edge":
            asyncio.run(generate_audio_edge(response, SAMPLE_FILE_NAME, VOICE))
            print("TTS ENGINE: Edge-tts")
        else:
            print("No valid TTS engine found")

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
                video = get_output_media(topic, SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER, LANDSCAPE, MUSIC_VOLUME, OUTPUTDIR)
                print(video)
            else:
                print("No background video after merging intervals")
        else:
            print("No background video")

    # Generate the specified number of videos
    for i in range(NUM_VIDS):
        print(f"Generating video {i+1} of {NUM_VIDS}")
        generate_video(SAMPLE_TOPIC)

        # If generating multiple videos, create a new topic for the next video
        if i < NUM_VIDS - 1:
            SAMPLE_TOPIC = generate_new_topic(SAMPLE_TOPIC, PROVIDER, MODEL)
            print(f"New topic generated: {SAMPLE_TOPIC}")

