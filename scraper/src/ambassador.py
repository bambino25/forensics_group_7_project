'''
This module is responsible for communicating with the LLM API.
It handles sending prompts, receiving responses, and formatting the data appropriately.
Attaching text files to the prompt is also supported.
'''
import requests
import json
import re
from bs4 import BeautifulSoup

class AmbassadorLLM:
    ''' 
    Talks with the LLM 
    - Establishes connections
    - Sends prompt
    - Makes sure the returned answer is in the right format
    '''
    def __init__(self, body):
        self.url = "http://localhost:11434/api/generate"
        self.body = body # {model, prompt, stream}
    
    def ask(self, prompt, attached_file=False):
        body = self.body.copy()
        if attached_file:
            body['prompt'] = self.merge_prompt_file(prompt, attached_file)
        else:
            body['prompt'] = f"{self.body['prompt']} \n\n '{prompt}'"
        response = requests.post(
            self.url,
            json=body
        )
        #print(response.request.body)
        if response.status_code != 200:
            # Throw an error if the response status code is not 200
            raise Exception(f"Error: Received status code {response.status_code} from LLM API")
        else:
            data = json.loads(response.text)
            return data['response']
    
    def merge_prompt_file(self, prompt, attached_file):
        with open(attached_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        cleaned_file_content = self.clean_text(soup.get_text())
        return f"{prompt}\n\n{"Here the html file:"}\n{cleaned_file_content}"
    
    def clean_text(self, text):
        # Remove non-alphanumeric characters (except spaces)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Replace multiple spaces and newlines with a single space
        text = re.sub(r'\s+', ' ', text).strip()
        return text

def test_ambassador():
    body = {
        "model": "gemma3:4b",
        "prompt": "Is the following text weapons, military equipment or gun types related? If it is - answer 'yes' if it is not - then answer 'no'",
        "stream": False,
    }
    ambassador = AmbassadorLLM(body)
    print(ambassador.ask("Is anyone here really stupid? Besides [them], of course.").strip())# No
    print(ambassador.ask("Is anyone here really stupid? Besides [them], of course that I want to kill with my fireweapon.").strip()) #Yes
    print(ambassador.ask("Is anyone here really stupid? Besides [them], of course that I want to kill with my ak-47.").strip()) #Yes
    
    print(ambassador.ask("Is anyone here really stupid? Besides [them], of course that I want to kill with my explosives.") .strip())# Yes
    print(ambassador.ask("Is anyone here really stupid? Besides [them], of course that I want to hug with my bullet.").strip()) #Yes
    print(ambassador.ask("Is anyone here really stupid? Besides [them], of course.").strip())# No
    