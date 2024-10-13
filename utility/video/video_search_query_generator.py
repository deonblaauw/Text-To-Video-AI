from openai import OpenAI
import os
import json
import re
from datetime import datetime
from utility.utils import log_response,LOG_TYPE_GPT

log_directory = ".logs/gpt_logs"

prompt = """# Instructions

Given the following video script and timed captions, extract three visually concrete and specific keywords for each time segment that can be used to search for background videos. The keywords should be short and capture the main essence of the sentence. They can be synonyms or related terms. If a caption is vague or general, consider the next timed caption for more context. If a keyword is a single word, try to return a two-word keyword that is visually concrete. If a time frame contains two or more important pieces of information, divide it into shorter time frames with one keyword each. Ensure that the time periods are strictly consecutive and cover the entire length of the video. Each keyword should cover between 2-4 seconds. The output should be in JSON format, like this: [[[t1, t2], ["keyword1", "keyword2", "keyword3"]], [[t2, t3], ["keyword4", "keyword5", "keyword6"]], ...]. Please handle all edge cases, such as overlapping time segments, vague or general captions, and single-word keywords.

For example, if the caption is 'The cheetah is the fastest land animal, capable of running at speeds up to 75 mph', the keywords should include 'cheetah running', 'fastest animal', and '75 mph'. Similarly, for 'The Great Wall of China is one of the most iconic landmarks in the world', the keywords should be 'Great Wall of China', 'iconic landmark', and 'China landmark'.

Important Guidelines:

Use only English in your text queries.
Each search string must depict something visual.
The depictions have to be extremely visually concrete, like rainy street, or cat sleeping.
'emotional moment' <= BAD, because it doesn't depict something visually.
'crying child' <= GOOD, because it depicts something visual.
The list must always contain the most relevant and appropriate query searches.
['Car', 'Car driving', 'Car racing', 'Car parked'] <= BAD, because it's 4 strings.
['Fast car'] <= GOOD, because it's 1 string.
['Un chien', 'une voiture rapide', 'une maison rouge'] <= BAD, because the text query is NOT in English.

Note: Your response should be the response only and no extra text or data.
  """

prompt2 = """

Get ready for some fascinating facts about mushrooms! 🍄
1. Mushrooms are not plants, they're part of the kingdom Fungi!
2. Some mushrooms can grow at an astonishing rate of 1 cm per hour!

# Instructions

Given the following video script and timed captions, extract three visually concrete and specific keywords for each time segment that can be used to search for background videos. The keywords should be short and capture the main essence of the sentence. They can be synonyms or related terms. If a caption is vague or general, consider the next timed caption for more context. If a keyword is a single word, try to return a two-word keyword that is visually concrete. If a time frame contains two or more important pieces of information, divide it into shorter time frames with one keyword each. Ensure that the time periods are strictly consecutive and cover the entire length of the video. Each keyword should cover between 2-4 seconds. The output should be in JSON format, like this: [[[t1, t2], ["keyword1", "keyword2", "keyword3"]], [[t2, t3], ["keyword4", "keyword5", "keyword6"]], ...]. Please handle all edge cases, such as overlapping time segments, vague or general captions, and single-word keywords.

For example, if the caption is 'The cheetah is the fastest land animal, capable of running at speeds up to 75 mph', the keywords should include 'cheetah running', 'fastest animal', and '75 mph'. Similarly, for 'The Great Wall of China is one of the most iconic landmarks in the world', the keywords should be 'Great Wall of China', 'iconic landmark', and 'China landmark'.

Let's say for example you receive the following Timed Captions:
((0, 0.34), 'Get ready')((0.34, 0.68), 'for some')((0.68, 1.1), 'fascinating')((1.1, 2.02), 'facts about')((2.02, 3.56), 'mushrooms One')((3.56, 4.74), 'mushrooms are')((4.74, 5.38), 'not plants')((5.38, 6.1), "They're part")((6.1, 6.66), 'of the kingdom')((6.66, 7.08), 'fungi Two')((7.08, 9.08), 'some mushrooms')((9.08, 9.28), 'can grow')((9.28, 9.66), 'at an')((9.66, 10.26), 'astonishing')((10.26, 10.7), 'rate of 1')((10.7, 11.44), 'centimeters per')((11.44, 12.22), 'hour Three')((12.22, 13.94)

And you receive the following Content Script: 
Get ready for some fascinating facts about mushrooms! 🍄
1. Mushrooms are not plants, they're part of the kingdom Fungi!
2. Some mushrooms can grow at an astonishing rate of 1 cm per hour!

The expected output should be the following:
[ [[0.0, 2.0], ["excited person"]], [[2.0, 4], ["mushrooms in forest"]], [[4, 7], ["many mushrooms in forest"]], [[7, 10], ["growing plant"]],  ]

Important Guidelines:

You must ensure that you consider all the Time Captions
You must combine multiple time captions into a longer timeframe, but never exceed a length of 5 seconds
Use only English in your text queries.
Each search string must depict something visual.
The depictions have to be extremely visually concrete, like rainy street, or cat sleeping.
'emotional moment' <= BAD, because it doesn't depict something visually.
'crying child' <= GOOD, because it depicts something visual.
The list must always contain the most relevant and appropriate query searches.
['Car', 'Car driving', 'Car racing', 'Car parked'] <= BAD, because it's 4 strings.
['Fast car'] <= GOOD, because it's 1 string.
['Un chien', 'une voiture rapide', 'une maison rouge'] <= BAD, because the text query is NOT in English.

Note: Your response should be the response only and no extra text or data.
"""


import re
import json

def fix_json(json_str):
    # Replace typographical apostrophes with straight single quotes
    json_str = json_str.replace("’", "'")
    
    # Replace mixed and incorrect quotes with double quotes
    json_str = json_str.replace("“", "\"").replace("”", "\"").replace("‘", "\"")
    
    # Handle the case for JSON backslashes by escaping them properly
    json_str = json_str.replace("\\", "\\\\")  # Escape any lone backslashes properly
    
    return json_str

def fix_json_content(content):
    # Fix improperly formatted strings, handling cases where single quotes should be preserved
    # Fixes specific issues like contractions or possessive apostrophes
    content = re.sub(r'(\w)"(\w)', r'\1\'\2', content)  # Fix "word"s" to "word's"
    
    # Replace stray single quotes with double quotes, but make sure we're not breaking contractions
    content = re.sub(r"(?<!\\)'", '"', content)  # Safely replace unescaped single quotes with double quotes

    # Fix escape sequences like backslashes (if needed)
    content = content.replace("\\", "\\\\")  # Escape any lone backslashes properly
    
    return content

def fix_quotes(content):
    # Ensure all quotes are correctly formatted, like "cow"s" to "cow's"
    content = re.sub(r'(\w)"(\w)', r'\1\'\2', content)
    return content

def getVideoSearchQueriesTimed(script, captions_timed, provider, model):
    # Assuming the end timestamp is the second value of the last tuple in captions_timed
    end = captions_timed[-1][0][1]
    try:
        out = [[[0, 0], ""]]  # Initialize output with a placeholder
        while out[-1][0][1] != end:
            content = call_OpenAI(script, captions_timed, provider, model)  # Fetch content
            
            # Step 1: Fix common JSON formatting issues
            content = fix_json(content)
            
            # Step 2: Handle additional content-specific issues
            content = fix_json_content(content)
            
            try:
                # Try parsing the content as JSON
                out = json.loads(content)
            except json.JSONDecodeError as e:
                print("Original content: \n", content, "\n\n")
                
                # Step 3: Remove formatting artifacts like markdown (```json blocks)
                content = content.replace("```json", "").replace("```", "")
                
                # Step 4: Attempt fixing problematic quotes again
                fixed_content = fix_quotes(content)
                print("Fixed content: \n", fixed_content, "\n\n")
                
                try:
                    # Try parsing the cleaned-up content again
                    out = json.loads(fixed_content)
                except json.JSONDecodeError as e_inner:
                    print("Still failing after fix:", e_inner)
                    return None
        
        # If everything works, return the parsed JSON
        return out
    except Exception as e:
        # Generic error handler
        print("Error in response:", e)
        return None







def call_OpenAI(script,captions_timed, provider, model):

    if provider == "groq":
        from groq import Groq
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            )
    elif provider == "openai":
        OPENAI_API_KEY = os.getenv('OPENAI_KEY')
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        print("[ERROR] No valid provider specified")

    user_content = """Script: {}
Timed Captions:{}
""".format(script,"".join(map(str,captions_timed)))
    print("Content", user_content)
    
    response = client.chat.completions.create(
        model= model,
        temperature=1,
        messages=[
            {"role": "system", "content": prompt2},
            {"role": "user", "content": user_content}
        ]
    )
    
    text = response.choices[0].message.content.strip()
    text = re.sub('\s+', ' ', text)
    print("Text", text)
    log_response(LOG_TYPE_GPT,script,text)
    return text

def merge_empty_intervals(segments):
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]
        if url is None:
            # Find consecutive None intervals
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            # Merge consecutive None intervals with the previous valid URL
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged
