import os
import json
import logging

from ..crawler.client import search_song, get_song
from ..crawler.client import get_artist_id, get_artist
from ..crawler.web import get_main, get_others

from dotenv import load_dotenv
from pymongo import MongoClient
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler

load_dotenv()

config = json.load(open("config.json"))
token = os.getenv('TOKEN') or config['token']
password = os.getenv('PASSWORD') or config['password']
port = os.getenv('PORT') or config['port']
dbname = os.getenv("DBNAME") or config['dbname']

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

client = MongoClient(config['db'].format(password, dbname))
db = client['lyrically']


def start(update, context):
    chat_id = update.effective_chat.id
    firstname = update['message']['chat']['first_name']
    lastname = update['message']['chat']['last_name']
    username = update['message']['chat']['username']
    if not db.users.find_one({'chat_id': chat_id}):
        db.users.insert_one({'chat_id': chat_id, 'recent_command': None,
                          "recent_search": None, "firstname": firstname,
                          'timestamp': datetime.utcnow(), "lastname": lastname,
                          'username': username})

    context.bot.send_message(chat_id=chat_id, text=config["msg"]["start"].format(firstname))
    context.bot.send_message(chat_id=chat_id, text=config["msg"]["menu"])


def song(update, context):
    chat_id = update.effective_chat.id
    update.message.reply_text(config['messages']['song'])
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "song"}})


def artist(update, context):
    chat_id = update.effective_chat.id
    update.message.reply_text(config['msg']['artist'])
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "artist"}})


def get_songs(text):
    rank = 1
    songs = search_song(text)
    update.message.reply_text("Enter song rank e.g: 1")
    for s in songs:
        update.message.reply_text(config['messages']['each_song'].format(s[1], s[2], rank))
        rank += 1
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "get_song"}})
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_search": songs}})


def get_artists(text):
    artists = get_artist_id(text)
    update.message.reply_text("Enter artist rank e.g: 1")
    for i in range(len(artists)):
        update.message.reply_text(config['msg']['each_artist'].format(artists.keys()[i], i+1))
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "get_artist"}})
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_search": artists}})


def article(update, context):
    chat_id = update.effective_chat.id
    articles = [get_main(), get_others()]
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_command": "article"}})
    db.users.update_one({"chat_id": chat_id},
                        {"$set": {"recent_search": articles}})

    rank = 1
    update.message.reply_text("Enter article rank to read article")
    update.message.reply_text("Main Article")
    update.message.reply_text(config['msg']['articles'].format(
        articles[0][1], rank
    ))
    rank += 1
    update.message.reply_text("Other Articles")
    for i in articles[1]:
        update.message.reply_text(config['msg']['articles'].format(
            i[1][0], rank
        ))
        rank += 1


def get_one_song(user, rank):
    songs = user['recent_search']
    rank -= 1
    s = songs[rank]
    song_id = s[0]
    s = get_song(id=song_id)
    update.message.reply_text(config['messages']['song_final'].format(s[1], s[5], s[2], s[3],
                                                                      s[4], s[6], s[0]))


def get_one_artist(user, rank):
    artists = user['recent_search']
    key = artists.keys()[rank-1]
    artist_id = artists[key]
    a = get_artist(artist_id)
    update.message.reply_text(config['msg']['artist_final1'].format(
        a[0], a[4], a[3], a[2]
    ))
    update.message.reply_text(config['msg']['artist_final2'].format(a[1]))


def get_one_article(user, rank):
    articles = user['recent_search']
    if rank == 1:
        a = articles[0]
        title = a[1]
        a = a[2]
        update.message.reply_text("Title: {}\n {}".format(title, a))
    else:
        aoa = articles[1]
        rank -= 2
        try:
            title = aoa[1][rank]
            a = aoa[2][rank]
            update.message.reply_text("Title: {}\n {}".format(title, a))
        except Exception as e:
            update.message.reply_text(config['msg']['unknown'])


def help_me(update, context):
    chat_id = update.effective_chat.id
    update.message.reply_text(config['messages']['help'])


def donate(update, context):
    chat_id = update.effective_chat.id
    update.message.reply_text(config['messages']['donate'])
    update.message.reply_text(config['messages']['menu'])


def hire(update, context):
    chat_id = update.effective_chat.id
    update.message.reply_text(config['messages']['hire'])


def echo(update, context):
    chat_id = update.effective_chat.id
    user = db.users.find_one({"chat_id": chat_id})
    recent_command = user["recent_command"]

    if recent_command == "song":
        text = update.message.text
        get_songs(text)
    elif recent_command == "get_song":
        rank = None
        try:
            rank = int(update.message.text)
        except Exception as e:
            update.message.reply_text(config['msg']['unknown'])
        get_one_song(user, rank)
    elif recent_command == "artist":
        text = update.message.text
        get_artists(text)
    elif recent_command == 'get_artist':
        rank = None
        try:
            rank = int(update.message.text)
        except Exception as e:
            update.message.reply_text(config['msg']['unknown'])
        get_one_artist(user, rank)
    elif recent_command == "article":
        rank = None
        try:
            rank = int(update.message.text)
        except Exception as e:
            update.message.reply_text(config['msg']['unknown'])
        get_one_article(user, rank)
    else:
        update.message.reply_text(config['msg']['unknown'])


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=config['msg']['unknown'])


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

song_handler = CommandHandler('song', song)
dispatcher.add_handler(song_handler)

artist_handler = CommandHandler('artist', artist)
dispatcher.add_handler(artist_handler)

article_handler = CommandHandler('article', article)
dispatcher.add_handler(article_handler)

help_handler = CommandHandler('help', help_me)
dispatcher.add_handler(help_handler)

hire_handler = CommandHandler('hire', hire)
dispatcher.add_handler(hire_handler)

donate_handler = CommandHandler('donate', donate)
dispatcher.add_handler(donate_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
# updater.start_webhook(listen="0.0.0.0",
#                       port=int(port),
#                       url_path=token)
# updater.bot.setWebhook("https://lyrically-bot.herokuapp.com/{}".format(token))
# updater.idle()
