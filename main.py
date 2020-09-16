#!/usr/bin/python3
# Author: @BlankGodd_

from emoji import emojize
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
from datetime import datetime
from search import Search_Genius

sg = Search_Genius()

config = json.load(open("config.json"))
token = config['token']
client = MongoClient(config['db'])
db = client['lyrically']
users_db = db.users

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    chat_id = update.effective_chat.id
    name = update["message"]["chat"]["first_name"]
    if not users_db.find_one({'chat_id': chat_id}):
        users_db.insert_one({'chat_id': chat_id, 'recent_command': None,
                             "recent_song_search": None,
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
                            {"$set": {"recent_song_search": songs}})
    elif recent_command == "get_song":
        text = update.message.text
        rank = text
        songs = user['recent_song_search']
        song = sg.get_song(songs=songs, rank=int(rank) - 1)
        context.bot.send_message(chat_id, text=config['messages']['song_final'].format(song['Title'],
                                                                                       song['Artist'],
                                                                                       song['recording_location'],
                                                                                       song['release_date'],
                                                                                       song['Description'],
                                                                                       song['Lyrics']))


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
song_handler = CommandHandler('songs', songs)
dispatcher.add_handler(song_handler)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
