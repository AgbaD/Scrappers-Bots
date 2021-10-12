#!usr/bin/python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('ACCESS_TOKEN')
base_url = "https://api.genius.com"


def search(query):
    path = 'search/'
    url = '/'.join([base_url, path])

    params = {'q': query}
    token = f'Bearer {access_token}'
    headers = {
        'Authorization': token,
        'application': 'BLyrics',
        'User-Agent': 'https://github.com/AgbaD/lyrically'
    }

    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code == 200:
        return resp.text
    return None


if __name__ == "__main__":
    print(search('cole'))
