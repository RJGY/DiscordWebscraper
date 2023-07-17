import requests
import json
from dotenv import load_dotenv

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = '332269999912132097'
CLIENT_SECRET = '937it3ow87i4ery69876wqire'

def retrieve_messages(channel_id, auth):
    headers = {
        'authorization' : auth
    }
    
    req = requests.get(f'{API_ENDPOINT}/channels/{channel_id}/messages', headers=headers)
    
    json_data = json.loads(req.text)
    for message in json_data:
        print(message)
        
def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
    r.raise_for_status()
    return r.json()

def refresh_token(refresh_token):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
    r.raise_for_status()
    return r.json()
    
        
retrieve_messages('1130422367802372118', 'MTEyMjQ2NjQyMzk3ODA2NjAxMg.GeeslP.pCmneZby_3aE1b9smVUDqR8T97i5Bwfz87M5Cg')
# this works