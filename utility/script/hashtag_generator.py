import os
from openai import OpenAI
import json
from utility.utils import fix_json_content , fix_json , fix_quotes

def generate_hashtags(llmscript,provider,model):

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

    prompt = (
        """You are a seasoned content writer for a YouTube Shorts channel, specializing in hashtags and trends. 
        Your hashtags are always on trend and concise. 
        They are incredibly engaging and appealing to a broad audience. 

        Keep it brief, highly interesting, and unique.

        Stictly output the trends in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {"trends": "#firsttrend #secondtrend #thirdtrend ..."}

        The following is a script that you need to carefully analyze, extract trands and output the hashtags in JSON format as previously described:
        """
    )

    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": llmscript}
            ]
        )
    content = response.choices[0].message.content
    # try:
    #     trends = json.loads(content)["trends"]
    # except Exception as e:
    #     json_start_index = content.find('{')
    #     json_end_index = content.rfind('}')
    #     print(content)
    #     content = content[json_start_index:json_end_index+1]
    #     trends = json.loads(content)["trends"]
    # return trends

            # Try to load the JSON content
    try:
        trends = json.loads(content)["trends"]
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw content: {content}")

        # Attempt to fix the JSON if there was an issue
        content = fix_json(content)
        content = fix_json_content(content)

        # Attempt JSON parsing again
        try:
            trends = json.loads(content)["trends"]
        except json.JSONDecodeError as e:
            print(f"Failed after attempting to fix JSON: {e}")
            return None

    return trends
