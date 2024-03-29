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
with open('code.txt', 'r', encoding='utf-8') as cfile:
    maincode=cfile.read()
with open('code_func.txt', 'r', encoding='utf-8') as funfile:
    code_fun=funfile.read()
newprompt = prompt +"\n" + maincode + "\n My constraints for this code are written as follows:"+ mycontent
newprompt = newprompt + "\n In this code, inputs were turned into parameters (like param1,param2),then code converted into function. You can also see its code below:" +code_fun
newprompt = newprompt + "\n Now, based on the constraint text for the first code, I want you to define constraint in the parameters so that the inputs are removed and affect the same variables in the function. Don't provide any explanation for these definitions. just write the constraint code for new parameters based on above defitions."
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": newprompt
        }
    ],
    model="gpt-4",
)
with open('result.txt', 'w', encoding='utf-8') as file:
    file.write(chat_completion.choices[0].message.content)
print(chat_completion.choices[0].message.content)