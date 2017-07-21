import json
import os.path
import time
import telegram
from telegram import User
from telegram.ext import Updater, CommandHandler, MessageHandler, typehandler, Filters

towork = True

def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this""")


if os.path.isfile("config.json"):
    config_file = open("config.json", "r")
    config = json.load(config_file)
    TOKEN = config["TOKEN"]
    config_file.close()
else:
    TOKEN = input("Enter TOKEN: ")
updater = Updater(TOKEN)
# Get the dispatcher to register handlers
dp = updater.dispatcher
# Add handlers for Telegram messages
help_handler = CommandHandler('help', c_help)
dp.add_handler(help_handler)
updater.start_polling()
updater.idle()
