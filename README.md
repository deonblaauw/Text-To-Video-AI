Here’s an updated `README.md` file reflecting the current code:

---

# Video Generation Script

This Python script automatically generates videos based on a given topic using various AI-driven components. The script integrates text generation, text-to-speech (TTS), background video selection, caption generation, and video rendering, making it an automated video production tool.

---

## Key Features

1. **AI-Powered Script Generation**:  
   Automatically generates video scripts based on the provided topic using AI models (OpenAI GPT).

2. **Text-to-Speech (TTS) Support**:  
   Converts generated scripts into speech using either OpenAI’s or Microsoft Edge’s TTS engine.

3. **Background Video Retrieval**:  
   Fetches background videos matching the script content from the Pexels video library.

4. **Caption Generation**:  
   Creates and times captions based on the generated audio.

5. **Video Effects (Experimental)**:  
   Optionally applies various video effects to the generated video (currently in the debug phase).

6. **Multi-Video Generation**:  
   Generates multiple videos in one execution, with the ability to create new topics for each video.

---

## Installation

1. **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up API Keys**:
   - **OpenAI**: Add your OpenAI API key.
   - **Edge TTS**: Ensure you have access to Microsoft Edge TTS services.

4. **Configure Video Server**:
   The script uses Pexels for background video retrieval. Ensure you have a Pexels API key configured in your environment.

---

## Usage

Run the script by providing a topic and desired options:

```bash
python app.py "Interesting facts about space" --num_vids 2 --landscape --tts openai --output_dir my_videos --duration 60
```

### Command-Line Arguments

- **`topic`** (required): The topic for the video.
- **`--landscape`** (optional): A flag to generate the video in landscape mode (default is portrait).
- **`--tts`** (optional): TTS engine to use (`openai` or `edge`, default is `openai`).
- **`--output_dir`** (optional): Directory to store the generated outputs (default is `generated_outputs`).
- **`--duration`** (optional): Duration of the video in seconds (default is 40 seconds).
- **`--num_vids`** (optional): Number of videos to generate (default is 1).

---

## Core Components

### Script Generation

The script uses OpenAI’s GPT model to generate a script based on the topic:

```python
generate_script(topic, provider, model, duration)
```

### Hashtag Generation

Automatically generates hashtags for social media platforms based on the script:

```python
generate_hashtags(script, provider, model)
```

### TTS (Text-to-Speech)

Depending on the selected engine, the script is converted into speech:

- **OpenAI TTS**:
    ```python
    generate_audio_openai(script, filename, voice)
    ```
- **Microsoft Edge TTS**:
    ```python
    generate_audio_edge(script, filename, voice)
    ```

### Caption Generation

Timed captions are generated based on the audio:

```python
generate_timed_captions(audio_filename)
```

### Background Video Search

Relevant background video URLs are retrieved from Pexels based on the generated script:

```python
getVideoSearchQueriesTimed(script, captions, provider, model)
generate_video_url(search_terms, server, orientation_landscape)
```

### Rendering the Final Video

All elements (script, audio, captions, and background videos) are combined and rendered into a final video:

```python
get_output_media(topic, audio_filename, captions, background_videos, video_server, landscape, music_volume_wav, music_volume_mp3, volume_tts, output_dir)
```

---

## Experimental Features

### Video Effects (In Development)

The script includes an experimental feature to apply video effects to the final video. This is currently in the debug phase and can be enabled manually by modifying the code. Available effects are defined in the `VIDEO_EFFECTS` list.

---

## Example Workflow

The script follows these steps:

1. **Generate the Script**: 
   A topic-based video script is created using OpenAI’s GPT model.
   
2. **Create Hashtags**: 
   Hashtags relevant to the script are generated.

3. **Generate TTS Audio**: 
   The script is converted into speech using either OpenAI or Edge TTS.

4. **Generate Captions**: 
   Captions are automatically generated and timed according to the TTS audio.

5. **Retrieve Background Videos**: 
   Relevant background videos are fetched using search queries based on the script content.

6. **Render the Final Video**: 
   All components are assembled into a single video file.

7. **Repeat for Additional Videos** (if requested): 
   If the `--num_vids` argument is greater than 1, the script generates new topics for each subsequent video, ensuring fresh content.

---

## Example

To generate a single 60-second landscape video about "Facts about submarines" using Microsoft Edge TTS and saving the outputs in a folder named `my_videos`:

```bash
python app.py "Facts about submarines" --num_vids 1 --landscape --tts edge --output_dir my_videos --duration 60
```

---

## Debugging & Development Notes

- The video effects feature is currently in a development/debugging phase and is not enabled by default.
- The script is designed to handle multi-video generation, but generating new topics after each video is still under development to ensure diversity.

---

## License

This project is licensed under the MIT License.

---

This `README.md` provides an overview of the script, its functionalities, how to install and use it, as well as some insights into its underlying structure and components.