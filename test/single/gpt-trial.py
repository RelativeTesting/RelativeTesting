from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()
client=OpenAI(
    api_key=os.getenv('GPT_API_KEY')
)
with open("prompt.txt", "r", encoding='utf-8') as promptfile:
    prompt = promptfile.read()
with open('trial.txt', 'r', encoding='utf-8') as file:
    mycontent = file.read()
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt +"\n"+ mycontent,
        }
    ],
    model="gpt-4",
)
print(chat_completion.choices[0].message.content)