#!/usr/bin/python3
# Author: @BlankGodd_

import json
from datetime import datetime
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import BadRequest
from pymongo import MongoClient
from emoji import emojize
from html_telegraph_poster import TelegraphPoster
from search import Search_Genius
from web import Webpage

sg = Search_Genius()
wp = Webpage()
t = TelegraphPoster(use_api=True)
t.create_api_token('Lyrically', 'Lyrically', 'https://github.com/BlankGodd/lyrically')


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


def articles(update, context):
    chat_id = update.effective_chat.id
    articles = wp.check_articles()
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "articles"}})
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_search": articles}})
    context.bot.send_message(chat_id, text="Enter article rank e.g: 1")
    for k in articles[0].keys():
        context.bot.send_message(chat_id,
                                 text="Headline: {} \nRank: 1".format(k))
    context.bot.send_message(chat_id,
                             text="Other News")
    rank = 2
    for k in articles[1].keys():
        context.bot.send_message(chat_id,
                                 text=config['messages']['articles'].format(k, rank))
        rank += 1


def help_me(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id,
                             text=emojize(config['messages']['help']))


def donate(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id,
                             text=emojize(config['messages']['donate']))
    context.bot.send_message(chat_id, text=emojize(config['messages']['menu']))


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
        rank = update.message.text
        songs = user['recent_search']
        song = sg.get_song(songs=songs, rank=int(rank) - 1)
        context.bot.send_message(chat_id, text=config['messages']['song_final'].format(song['Title'],
                                                                                       song['Artist'],
                                                                                       song['recording_location'],
                                                                                       song['release_date'],
                                                                                       song['Description']))
        try:
            context.bot.send_message(chat_id, text="Lyrics: {}".format(song['Lyrics']))
        except BadRequest:
            context.bot.send_message(chat_id, text="Lyrics too long. You will be sent a link to a webpage. Thanks")
            path_url = t.post(title=song['Title'], author="Lyrically", text=song['Lyrics'])
            url = path_url['url']
            context.bot.send_message(chat_id, text="Lyrics: {}".format(url))
        context.bot.send_message(chat_id, text=emojize(config['messages']['menu']))
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
        rank = update.message.text
        artists = user['recent_search']
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
        context.bot.send_message(chat_id, text=f"Songs by {artist['artist_name']}")
        for val in artist['songs'].values():
            context.bot.send_message(chat_id, text=val)
        context.bot.send_message(chat_id, text=emojize(config['messages']['menu']))
    elif recent_command == "articles":
        rank = update.message.text
        articles = user['recent_search']
        if rank == '1':
            for k, v in articles[0].items():
                article = wp.get_article(v)
                context.bot.send_message(chat_id,
                                         text="Title: {}\n {}".format(k, article))
        else:
            titles = [k for k in articles[1].keys()]
            links = [v for v in articles[1].values()]
            rank = int(rank) - 2
            article = wp.get_article(links[rank])
            title = titles[rank]
            context.bot.send_message(chat_id,
                                     text="Title: {}\n {}".format(title, article))
        context.bot.send_message(chat_id, text=emojize(config['messages']['menu']))


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
song_handler = CommandHandler('songs', songs)
dispatcher.add_handler(song_handler)
artist_handler = CommandHandler('artist', artist)
dispatcher.add_handler(artist_handler)
articles_handler = CommandHandler('articles', articles)
dispatcher.add_handler(articles_handler)
help_handler = CommandHandler('help', help_me)
dispatcher.add_handler(help_handler)
donate_handler = CommandHandler('donate', donate)
dispatcher.add_handler(donate_handler)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
