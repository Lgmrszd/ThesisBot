import json
import os.path
import time
import telegram
import dbconfig
from telegram import User
from telegram.ext import Updater, CommandHandler, MessageHandler, typehandler, Filters


def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this
/thesis thesisname - Not realized yet""")


def thesis(bot, update, args):
    message = update.message
    if len(args) == 0:
        print("NOT OK")
        bot.sendMessage(chat_id=message.chat_id,
                        text="Need text")
    elif message.chat.type == "private":
        bot.sendMessage(chat_id=message.chat_id,
                        text="This command for chats only")
    else:
        print("OK")
        user = update.message.from_user
        bot.sendMessage(chat_id=message.chat_id,
                        text="chat id: %s, user id: %s, username: %s, chat type: %s\n"%(message.chat.id, user.id, user.username, message.chat.type)+\
                        "args: "+" ".join(args))
        print("INSERTING USER")
        dbuser = dbconfig.getUser(user.id)
        if not dbuser:
            print("ADDING USER")
            dbconfig.insertUser(user_id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name)
        else:
            print("ALREADY HAVE THAT USER")
        print("INSERTING THESIS")
        dbconfig.insertThesis(init_id=message.message_id, chat_id=message.chat.id, user_id=user.id, body=" ".join(args))
        print("DONE")


TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise EnvironmentError("TOKEN not found")
updater = Updater(TOKEN)
# Get the dispatcher to register handlers
dp = updater.dispatcher
# Add handlers for Telegram messages
help_handler = CommandHandler('help', c_help)
dp.add_handler(help_handler)
thesis_handler = CommandHandler('thesis', thesis, pass_args=True)
dp.add_handler(thesis_handler)
updater.start_polling()
updater.idle()
