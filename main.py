import json
import os.path
import time
import telegram
from telegram import User
from telegram.ext import Updater, CommandHandler, MessageHandler, typehandler, Filters


def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this
/thesis thesisname - Not realized yet""")


def thesis(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="IN DEVELOPMENT SORRY")

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise EnvironmentError("TOKEN not found")
updater = Updater(TOKEN)
# Get the dispatcher to register handlers
dp = updater.dispatcher
# Add handlers for Telegram messages
help_handler = CommandHandler('help', c_help)
dp.add_handler(help_handler)
help_handler = CommandHandler('help', c_help)
dp.add_handler(help_handler)
updater.start_polling()
updater.idle()
