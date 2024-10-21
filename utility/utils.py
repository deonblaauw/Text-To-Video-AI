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


import os

def save_video_description_to_file(sample_topic, script, hashtags, output_directory):
    # Create the directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Limit the filename to 40 characters and replace spaces with underscores
    filename_base = sample_topic.replace(" ", "_")[:40]

    # Set the initial full path for the file
    full_path = os.path.join(output_directory, filename_base + ".txt")

    # Check if the file already exists, and append a number if necessary
    counter = 1
    while os.path.exists(full_path):
        # If the file exists, append a counter to the filename before the extension
        full_path = os.path.join(output_directory, f"{filename_base}_{counter}.txt")
        counter += 1

    try:
        # Save the script and hashtags to the file
        with open(full_path, 'w') as f:
            # f.write("Description:\n")
            f.write(script + "\n\n")
            f.write("Hashtags:\n")
            f.write(hashtags + "\n\n")
        print(f"Response and hashtags successfully saved to {full_path}")
    except Exception as e:
        print(f"Error saving to file: {e}")




import re
import json

def fix_json(json_str):
    # Escape unescaped backslashes (i.e., backslashes that are not part of an existing escape sequence)
    json_str = re.sub(r'(?<!\\)\\(?![\\"])', r"\\\\", json_str)

    # Remove trailing commas in JSON arrays and objects
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)

    return json_str

def fix_json_content(content):
    # Fix improperly formatted strings, handling cases where single quotes should be preserved
    content = re.sub(r'(\w)"(\w)', r'\1\'\2', content)  # Fix "word"s" to "word's"
    
    # Replace stray single quotes with double quotes in keys/values
    content = re.sub(r'(?<=[:,\s])\'(?=\w+\'?\s*[:,\]])', '"', content)  # Replace single quotes in keys/values

    # Replace \\n with actual newlines (\n)
    content = content.replace("\\n", "\n")
    
    return content


def fix_quotes(content):
    # Ensure all quotes are correctly formatted around JSON keys/values
    content = re.sub(r'(?<=[:,\s])\'(?=\w+\'?\s*[:,\]])', '"', content)
    return content


