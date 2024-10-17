from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import painting
import subprocess
import cv2
import sys

VIDEO_EFFECTS = {
    # "pencil_sketch": {"type": "ffmpeg", "command": "curves=preset=cross_process,edgedetect=low=0.1:high=0.4"},
    # "painting": {"type": "moviepy", "params": {"saturation": 1.4, "black": 0.006}},
    # "cartoon": {"type": "cv2", "params": {}},  # Additional parameters can be added if needed
    "cartoon": {"type": "torch", "params": {}}  # Additional parameters can be added if needed
}



def apply_video_effect(video_url, effect_name, output_file):
    """
    Apply the specified video effect using either FFmpeg, MoviePy, or OpenCV.

    Args:
        video_url (str): URL or path to the input video.
        effect_name (str): The name of the video effect to apply.
        output_file (str): The path to save the output video.
    """
    # Check if the effect exists in the dictionary
    if effect_name not in VIDEO_EFFECTS:
        print(f"Effect '{effect_name}' not found.")
        return
    
    effect = VIDEO_EFFECTS[effect_name]
    
    # Check if the effect is an ffmpeg effect
    if effect["type"] == "ffmpeg":
        filter_command = effect["command"]
        cmd = [
            'ffmpeg', '-i', video_url,
            '-vf', filter_command,
            '-y',  # Overwrite output if it exists
            output_file
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Effect '{effect_name}' applied successfully. Output saved to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error applying effect '{effect_name}': {e}")
    
    # Check if the effect is a moviepy effect
    elif effect["type"] == "moviepy":
        apply_moviepy_effect(video_url, output_file , effect_name)

    # Check if the effect is a cv2 effect
    elif effect["type"] == "cv2":
        apply_cv2_effect(video_url, output_file , effect_name)

    elif effect["type"] == "torch":
        apply_torch_effect(video_url, output_file , effect_name)


def apply_torch_effect(video_url, output_file , effect_name):
    effect = VIDEO_EFFECTS[effect_name]

    

    print(f"Effect '{effect_name}' applied successfully using Torch. Output saved to {output_file}")

def apply_moviepy_effect(video_url, output_file , effect_name):
    effect = VIDEO_EFFECTS[effect_name]

    clip = VideoFileClip(video_url)
    params = effect["params"]
    painted_clip = painting(clip, saturation=params.get("saturation", 1.4), black=params.get("black", 0.006))
    painted_clip.write_videofile(output_file, codec="libx264")

    print(f"Effect '{effect_name}' applied successfully using MoviePy. Output saved to {output_file}")

def apply_cv2_effect(video_url, output_file , effect_name):
    """
    Apply a cartoon effect to a video using OpenCV.

    Args:
        video_url (str): URL or path to the input video.
        output_file (str): The path to save the output video.
    """
    # Open the video
    cap = cv2.VideoCapture(video_url)
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Initialize the video writer
    video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc('D','I','V','X'), fps, (width, height))

    # Loop through each frame
    for frame_idx in range(total_frames):
        # Read each frame
        ret, frame = cap.read()
        if not ret:
            break  # Exit the loop if no frames are left

        # Convert the video into a cartoon styled effect
        cartoon_image = cv2.stylization(frame, sigma_s=150, sigma_r=0.25)

        # Write (save) out frame
        video_writer.write(cartoon_image)

        # Calculate and print progress
        percent_complete = (frame_idx + 1) / total_frames * 100
        sys.stdout.write(f"\rProcessing... {percent_complete:.2f}% complete")
        sys.stdout.flush()

        # Break the loop when you press the 'Q' key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    print(f"Effect '{effect_name}' applied successfully using cv2. Output saved to {output_file}")