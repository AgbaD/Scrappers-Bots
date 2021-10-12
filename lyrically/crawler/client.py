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


def search_song(query):
    songs = get_hits(query)
    result = []
    for song in songs:
        song_id = song['result']['id']
        song_title = song['result']['full_title']
        artist = song['result']['primary_artist']['name']
        s = (song_id, song_title, artist)
        result.append(s)
    return result


def get_song(id):
    path = f"songs/{id}"
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
    song = json.loads(resp.text)

    base = song['response']['song']
    description = base['description']['plain']
    title = base['full_title']
    recording_location = base['recording_location']
    release_date = base['release_date_for_display']
    lyrics_url = base['url']
    artist = base['album']['artist']['name']
    album_title = base['album']['name']
    album_id = base['album']['id']

    song = [description, title, recording_location, release_date, lyrics_url, artist, album_title, album_id]
    return song


def get_album(id):
    path = f"albums/{id}"
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
    album = json.loads(resp.text)
    title = album['response']['album']['full_title']
    release_date = album['response']['album']['release_date']
    return [title, release_date]


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


