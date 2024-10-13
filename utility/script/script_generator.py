import os
import groq
from openai import OpenAI
import json
from utility.utils import fix_json_content , fix_json , fix_quotes


import json
import re
import os
from openai import OpenAI

def generate_script(topic, provider, model, vid_time):
    vid_length = float(vid_time) * 2.8

    print("Instructions for video time is", vid_time, "seconds ~", vid_length, "words in length")

    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    elif provider == "openai":
        OPENAI_API_KEY = os.getenv('OPENAI_KEY')
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        print("[ERROR] No valid provider specified")
        return None

    # Construct prompt using vid_time and vid_length
    prompt = f"""
        You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
        Your facts shorts are concise, each lasting approximately equal to but slightly less than {vid_time} seconds (approximately {vid_length} words). It's vital that you attempt to reach the desired word count of {vid_length}.
        
        They are incredibly engaging and original. When a user requests a specific type of facts short, you will create it.

        For instance, if the user asks for:
        Weird facts
        You would produce content like this:

        Weird facts you don't know:
        - Bananas are berries, but strawberries aren't.
        - A single cloud can weigh over a million pounds.
        - There's a species of jellyfish that is biologically immortal.
        - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.
        - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.
        - Octopuses have three hearts and blue blood.

        You are now tasked with creating the best short script based on the user's requested type of 'facts'.

        Keep it brief, highly interesting, and unique.

        Stictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {{"script": "Here is the script ..."}}
    """

    try:
        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
        content = response.choices[0].message.content

        # Try to load the JSON content
        try:
            script = json.loads(content)["script"]
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw content: {content}")

            # Attempt to fix the JSON if there was an issue
            content = fix_json(content)
            content = fix_json_content(content)

            # Attempt JSON parsing again
            try:
                script = json.loads(content)["script"]
            except json.JSONDecodeError as e:
                print(f"Failed after attempting to fix JSON: {e}")
                return None

        return script

    except Exception as e:
        print(f"An error occurred during script generation: {e}")
        return None




def generate_new_topic(topic,provider,model):

    print("Generating new topic from: ", topic)

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
        """You receive a topic, and must create a similar sentence, of more or less the same length, just focused on a different but semi-related topic

        Keep it brief, highly interesting, and on-trend.

        Stictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'topic'.

        # Output
        {"topic": "Here is the topic you generated for the user ..."}
        """
    )

    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        new_topic = json.loads(content)["topic"]
    except Exception as e:
        json_start_index = content.find('{')
        json_end_index = content.rfind('}')
        print(content)
        content = content[json_start_index:json_end_index+1]
        new_topic = json.loads(content)["topic"]
    return new_topic
