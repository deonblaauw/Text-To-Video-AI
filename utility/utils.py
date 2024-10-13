import os
from datetime import datetime
import json

# Log types
LOG_TYPE_GPT = "GPT"
LOG_TYPE_PEXEL = "PEXEL"

# log directory paths
DIRECTORY_LOG_GPT = ".logs/gpt_logs"
DIRECTORY_LOG_PEXEL = ".logs/pexel_logs"

# method to log response from pexel and openai
def log_response(log_type, query,response):
    log_entry = {
        "query": query,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    if log_type == LOG_TYPE_GPT:
        if not os.path.exists(DIRECTORY_LOG_GPT):
            os.makedirs(DIRECTORY_LOG_GPT)
        filename = '{}_gpt3.txt'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        filepath = os.path.join(DIRECTORY_LOG_GPT, filename)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry) + '\n')

    if log_type == LOG_TYPE_PEXEL:
        if not os.path.exists(DIRECTORY_LOG_PEXEL):
            os.makedirs(DIRECTORY_LOG_PEXEL)
        filename = '{}_pexel.txt'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        filepath = os.path.join(DIRECTORY_LOG_PEXEL, filename)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry) + '\n')


def save_video_description_to_file(filename, script, hashtags, output_directory):
    # Create the generated_outputs directory if it doesn't exist
    # output_directory = "generated_outputs"
    os.makedirs(output_directory, exist_ok=True)  # Creates the directory if it doesn't exist

    # Update the filename to include the directory path
    full_path = os.path.join(output_directory, filename)

    try:
        with open(full_path, 'w') as f:
            f.write("Description:\n")
            f.write(script + "\n\n")
            f.write("Hashtags:\n")
            f.write(hashtags + "\n\n")
        print(f"Response and hashtags successfully saved to {full_path}")
    except Exception as e:
        print(f"Error saving to file: {e}")

