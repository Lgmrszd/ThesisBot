import os.path
import datetime
import dbconnect
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


def gen_kb():
    m30 = InlineKeyboardButton("30 minutes", callback_data="lt:00:30:00")
    h1 = InlineKeyboardButton("1 hour", callback_data="lt:01:00:00")
    h5 = InlineKeyboardButton("5 hours", callback_data="lt:05:00:00")
    h10 = InlineKeyboardButton("10 hours", callback_data="lt:10:00:00")
    h24 = InlineKeyboardButton("1 day", callback_data="lt:24:00:00")
    d = InlineKeyboardButton("DELET THIS", callback_data="DELETE")
    kb = InlineKeyboardMarkup(inline_keyboard=[[m30, h1, h5, h10, h24], [d]])
    return kb


def thesisToText(text, stime, t_id):
    return ("\n"
            "✅ %s \n"
            "~ published at %s, id %d \n"
            "\n") % (text, stime, t_id)


def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this
/thesis thesis text - add new thesis
/lt - get latest theses""")


def fromUTCtoTZ(dt):
    tz = datetime.timezone(datetime.timedelta(hours=3))
    return dt.astimezone(tz)


class ThesisBot:
    def __init__(self, token, bot_db):
        self.__token = token
        self.__bot_db = bot_db
        self.__updater = Updater(token, user_sig_handler=self.stop_all)
        self.__dp = self.__updater.dispatcher

    def add_command_handler(self, command, callback):
        ch = CommandHandler(command, callback)
        self.__dp.add_handler(ch)

    def stop_all(self, signum, frame):
        print("STOPPING, signal:", signum)
        self.__bot_db.close()

