import edge_tts
import requests
import os

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text,"en-AU-WilliamNeural")
    await communicate.save(outputFilename)


# Async function to generate audio using OpenAI TTS
async def generate_audio_openai(text, outputFilename):
    api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is stored in an environment variable
    url = "https://api.openai.com/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy"
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


