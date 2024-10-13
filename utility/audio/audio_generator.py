import edge_tts
import requests
import os
import random

async def generate_audio_edge(text, outputFilename, voice):
    
    available_voices = [
    "en-AU-NatashaNeural",
    "en-AU-WilliamNeural",
    "en-CA-ClaraNeural",
    "en-CA-LiamNeural",
    "en-HK-SamNeural",
    "en-HK-YanNeural",
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
    "en-IE-ConnorNeural",
    "en-IE-EmilyNeural",
    "en-KE-AsiliaNeural",
    "en-KE-ChilembaNeural",
    "en-NZ-MitchellNeural",
    "en-NZ-MollyNeural",
    "en-NG-AbeoNeural",
    "en-NG-EzinneNeural",
    "en-PH-JamesNeural",
    "en-PH-RosaNeural",
    "en-SG-LunaNeural",
    "en-SG-WayneNeural",
    "en-ZA-LeahNeural",
    "en-ZA-LukeNeural",
    "en-TZ-ElimuNeural",
    "en-TZ-ImaniNeural",
    "en-GB-LibbyNeural",
    "en-GB-MaisieNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
    "en-GB-ThomasNeural",
    "en-US-AriaNeural",
    "en-US-AnaNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-MichelleNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural"
    ]

    # Check if the provided voice is valid; if not, choose a random one
    if voice not in available_voices:
        voice = random.choice(available_voices)
        print(f"No voice specified by user. Using random voice: {voice}")

    
    communicate = edge_tts.Communicate(text, voice)


    await communicate.save(outputFilename)

# Async function to generate audio using OpenAI TTS
async def generate_audio_openai(text, outputFilename, voice):
    api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is stored in an environment variable
    url = "https://api.openai.com/v1/audio/speech"

    # List of available voices
    available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    # Check if the provided voice is valid; if not, choose a random one
    if voice not in available_voices:
        voice = random.choice(available_voices)
        print(f"No voice specified by user. Using random voice: {voice}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "tts-1",
        "input": text,
        "voice": voice  # Use the validated or random voice
    }

    # Make a POST request to OpenAI API
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the audio to the output file
        with open(outputFilename, "wb") as audio_file:
            audio_file.write(response.content)
        print(f"Audio generated and saved as '{outputFilename}'")
    else:
        # Handle API errors
        print(f"Failed to generate audio. Status code: {response.status_code}")
        print(f"Response: {response.text}")
