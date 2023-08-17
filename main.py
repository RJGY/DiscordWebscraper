import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

API_ENDPOINT = 'https://discord.com/api/v10'
CHANNEL_IDS = json.loads(os.environ.get('CHANNEL_IDS'))
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')

format_string = "%Y-%m-%dT%H:%M:%S.%f"

def retrieve_messages(channel_id, auth):
    headers = {
        'authorization' : auth
    }
    
    req = requests.get(f'{API_ENDPOINT}/channels/{channel_id}/messages', headers=headers)
    
    json_data = json.loads(req.text)
    json_data = json_data[::-1]
    # for message in json_data:
    #     print(message)
    # print(type(json_data[0]))
    return json_data

def save_to_file(data):
    with open('messages.txt', 'w') as f:
        for message in data:
            timestamp = message.get('timestamp')[:-6]
            author = message.get('author').get('username')
            content = message.get('content')
            f.write(timestamp + ' ' + author + ': ' + content + '\n')

def read_from_file():
    with open('messages.txt', 'r') as f:
        res = []
        for line in f:
            res.append(line[:-1])
        return res
            
def parse_plain_messages(messages):
    list_of_dict_messages = []
    for message in messages:
        dict_messages = {}
        timestamp, author, content = message.split(' ', 2)
        dict_messages['timestamp'] = timestamp
        dict_messages['author'] = author
        dict_messages['content'] = content
        list_of_dict_messages.append(dict_messages)
    return list_of_dict_messages


def convert_timestamp_to_int(timestamp):
    time = datetime.strptime(timestamp, format_string)
    int_time = int(time.timestamp())
    return int_time

def trim_data(data, last_message):
    last_message_time = convert_timestamp_to_int(last_message)
    for i in range(len(data)):
        if convert_timestamp_to_int(data[i].get('timestamp')) == last_message_time:
            return data[i+1:]
    return data

def main():
    pass

data = retrieve_messages('1140562562065387572', AUTH_TOKEN)
save_to_file(data)
messages = read_from_file()
print(parse_plain_messages(messages))
new_messages = trim_data(parse_plain_messages(messages), '2023-08-14T08:30:16.397000')
print(new_messages)
# print(parse_plain_messages(messages))
# convert_timestamp_to_int('2023-08-14T08:28:28.836000')