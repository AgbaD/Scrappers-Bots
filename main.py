#!/usr/bin/python3
# Author: @BlankGodd_

from emoji import emojize
import os
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
from datetime import datetime


config = json.load(open("config.json"))
token = config['token']
# client = MongoClient(config['db'])
# db = client['blyrics']
# users_db = db.users

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    chat_id = update.effective_chat.id
    name = update["message"]["chat"]["first_name"]
    """if not users_db.find_one({'chat_id': chat_id}):
        users_db.insert_one({'chat_id': chat_id, 'recent_command': None,
                             'timestamp': datetime.utcnow()})"""
    context.bot.send_message(chat_id,
                             text=emojize(config['messages']['start'].format(name)))
    context.bot.send_message(chat_id, text=emojize(config['messages']['menu']))


def echo(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text
    print(text)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
