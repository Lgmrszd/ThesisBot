import json
import os.path
import telegram
from telegram import User
from telegram.ext import Updater, CommandHandler, MessageHandler, typehandler, Filters


def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this""")


def main():
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
    start_handler = CommandHandler('help', c_help)
    dp.add_handler(start_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
