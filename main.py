#!/usr/bin/python3
# Author: @BlankGodd_

from emoji import emojize
import json
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
from datetime import datetime
from search import Search_Genius

sg = Search_Genius()

config = json.load(open("config.json"))
token = os.environ.get('TOKEN')
client = MongoClient(config['db'])
db = client['lyrically']
users_db = db.users

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    chat_id = update.effective_chat.id
    name = update["message"]["chat"]["first_name"]
    if not db.users.find_one({'chat_id': chat_id}):
        db.users.insert_one({'chat_id': chat_id, 'recent_command': None,
                             "recent_search": None,
                             'timestamp': datetime.utcnow()})
    context.bot.send_message(chat_id,
                             text=emojize(config['messages']['start'].format(name)))
    context.bot.send_message(chat_id, text=emojize(config['messages']['menu']))


def songs(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id,
                             text=emojize(config['messages']['song']))
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "song"}})


def artist(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id,
                             text=emojize(config['messages']['artist']))
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "artist"}})


def echo(update, context):
    chat_id = update.effective_chat.id
    user = db.users.find_one({"chat_id": chat_id})
    recent_command = user["recent_command"]

    if recent_command == "song":
        text = update.message.text
        rank = 0
        songs = sg.search_song(search_str=text)
        context.bot.send_message(chat_id, text="Enter song rank e.g: 1")
        for song in songs:
            context.bot.send_message(chat_id,
                                     text=config['messages']['each_song'].format(song[0], song[2], rank + 1))
            rank += 1
        db.users.update_one({"chat_id": chat_id},
                            {"$set": {"recent_command": "get_song"}})
        db.users.update_one({"chat_id": chat_id},
                            {"$set": {"recent_search": songs}})
    elif recent_command == "get_song":
        text = update.message.text
        rank = text
        songs = user['recent_search']
        song = sg.get_song(songs=songs, rank=int(rank) - 1)
        context.bot.send_message(chat_id, text=config['messages']['song_final'].format(song['Title'],
                                                                                       song['Artist'],
                                                                                       song['recording_location'],
                                                                                       song['release_date'],
                                                                                       song['Description']))
        context.bot.send_message(chat_id, text="Lyrics: {}".format(song['Lyrics']))
    elif recent_command == 'artist':
        text = update.message.text
        artists = sg.search_artist(search_str=text)
        context.bot.send_message(chat_id, text="Enter artist rank e.g: 1")
        for i in range(5):
            context.bot.send_message(chat_id, text=config['messages']['each_artist'].format(artists[i][0], i + 1))
        db.users.update_one({"chat_id": chat_id},
                            {"$set": {"recent_command": "get_artist"}})
        db.users.update_one({"chat_id": chat_id},
                            {"$set": {"recent_search": artists}})
    elif recent_command == "get_artist":
        text = update.message.text
        artists = user['recent_search']
        rank = text
        artist = sg.get_artist_info(all_artist=artists, rank=int(rank) - 1)
        context.bot.send_message(chat_id,
                                 text=config['messages']['artist_final1'].format(artist['artist_name'],
                                                                                 artist['Aliases'],
                                                                                 artist['Twitter Handle'],
                                                                                 artist['Instagram Handle'],
                                                                                 artist['Facebook Name']))
        context.bot.send_message(chat_id,
                                 text=config['messages']['artist_final2'].format(artist['Description'],
                                                                                 artist['image_url']))
        context.bot.send_message(chat_id,
                                 text="Songs: {}".format(artist['songs']))


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
song_handler = CommandHandler('songs', songs)
dispatcher.add_handler(song_handler)
artist_handler = CommandHandler('artist', artist)
dispatcher.add_handler(artist_handler)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
