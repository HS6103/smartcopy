import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Set your API key here
openai_api_key = os.getenv("openai_api_key")

# Set up the client
client = OpenAI(api_key=openai_api_key)


# def _translate_to_english(text):
#     """Translates Traditional Chinese to English using OpenAI."""
#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a professional news translator."},
#             {"role": "user", "content": f"Translate the following Traditional Chinese news report to fluent English:\n\n{text}"}
#         ]
#     )
#     return response.choices[0].message.content.strip()

def _summarize_to_ap_style(original_text, lead, word_limit=300):
    """Summarizes text to AP style news story with given lead and word limit."""
    prompt = (
        f"{original_text}\n\n"
        f"Task: based on above report, finish the story after the given English lead, return story with given lead, Constraint: [AP style, reverse pyramid structure], Word limit: {word_limit}, English lead:\n\n{lead}"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert AP-style news writer, using concise, straight-forward plain English."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def process_news_story(chinese_text, lead):
    """Processes a Chinese news story, translating it to English and summarizing it to AP style."""
    summary = _summarize_to_ap_style(chinese_text, lead)
    
    return summary


