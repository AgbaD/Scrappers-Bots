#!usr/bin/python3

import os
import json
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


def get_hits(query):
    result = json.loads(search(query))
    return result["response"]["hits"]


def get_artist_id(artist):
    result = get_hits(artist)
    ans = {}
    for a in result:
        name = a["result"]["primary_artist"]["name"]
        id = a["result"]["primary_artist"]["id"]
        ans[name] = id
    return ans


def get_artist(id):
    path = f"artists/{id}"
    url = '/'.join([base_url, path])

    params = {'text_format': 'plain'}
    token = f'Bearer {access_token}'
    headers = {
        'Authorization': token,
        'application': 'BLyrics',
        'User-Agent': 'https://github.com/AgbaD/lyrically'
    }

    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code != 200:
        return None
    art = json.loads(resp.text)
    names = art["response"]["artist"]["alternate_names"]
    description = art["response"]["artist"]["description"]["plain"]
    facebook_name = art["response"]["artist"]["facebook_name"]
    instagram_name = art["response"]["artist"]["instagram_name"]
    twitter_name = art["response"]["artist"]["twitter_name"]
    return names, description, facebook_name, instagram_name, twitter_name


if __name__ == "__main__":
    idd = get_artist_id('drake')
    print(idd)
    for v in idd.values():
        print(get_artist(v))
