import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_ENDPOINT = 'https://discord.com/api/v10'
CHANNEL_IDS = json.loads(os.environ.get('CHANNEL_IDS'))
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')

def retrieve_messages(channel_id, auth):
    headers = {
        'authorization' : auth
    }
    
    req = requests.get(f'{API_ENDPOINT}/channels/{channel_id}/messages', headers=headers)
    
    json_data = json.loads(req.text)
    json_data = json_data[::-1]
    for message in json_data:
        print(message)
    print(type(json_data[0]))
    return json_data

def save_to_file(data):
    with open('messages.txt', 'w') as f:
        for message in data:
            f.write(message.get('timestamp') + ' ' + message.get('author').get('username') + ' ' + message.get('content') + '\n')
            
        
data = retrieve_messages('1140562562065387572', AUTH_TOKEN)
save_to_file(data)