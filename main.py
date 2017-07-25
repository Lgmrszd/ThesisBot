import os.path
import datetime
import dbconfig
import logging
from telegram import User, InlineQueryResultArticle, InputTextMessageContent, KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, InlineQueryHandler

logging.basicConfig(format='[%(asctime)s][%(levelname)s]:%(message)s', level=logging.DEBUG, datefmt='%d.%m.%Y %H:%M:%S')


def thesisToText(interval, text, stime):
    return ("\n"
            "—— ‼️ Theses in last %s ‼️ ——\n"
            "\n"
            "✅ %s \n"
            "~ published at %s \n"
            "\n"
            "—— end of thesis ——") % (interval, text, stime)


def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this
/thesis thesis text
/last30minsTheses - get theses for last 30 minutes
/last5hoursTheses - get theses for last 5 hours""")


def fromUTCtoTZ(dt):
    tz = datetime.timezone(datetime.timedelta(hours=3))
    return dt.astimezone(tz)


def last30minsTheses(bot, update):
    message = update.message
    theses = dbconfig.getLast30minsTheses(message.chat_id)
    str_theses = []
    for t in theses:
        stime = fromUTCtoTZ(t['creation_time']).strftime('%m.%d %H:%M:%S')
        tbody = t['body']
        st = thesisToText("30 minutes", tbody, st)
        str_theses.append(st)
    bot.sendMessage(chat_id=message.chat_id,
                    text="Theses in last 30 minutes:\n\n" + "\n".join(str_theses))


def last5hoursTheses(bot, update):
    message = update.message
    theses = dbconfig.getLast5hoursTheses(message.chat_id)
    str_theses = []
    for t in theses:
        stime = fromUTCtoTZ(t['creation_time']).strftime('%Y-%m-%d %H:%M:%S')
        tbody = t['body']
        st = "thesis time: %s\ntext:\n%s" % (stime, tbody)
        str_theses.append(st)
    bot.sendMessage(chat_id=message.chat_id,
                    text="Theses in last 5 hours:\n\n" + "\n".join(str_theses))


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
        print("INSERTING USER")
        dbuser = dbconfig.getUserById(user.id)
        if not dbuser:
            print("ADDING USER")
            dbconfig.insertUser(user_id=user.id, username=user.username, first_name=user.first_name,
                                last_name=user.last_name)
        else:
            print("ALREADY HAVE THAT USER")
        print("INSERTING THESIS")
        dbthesis = dbconfig.getThesisByBody(" ".join(args))
        if not dbthesis:
            print("ADDING THESIS")
            dbconfig.insertThesis(init_id=message.message_id, chat_id=message.chat.id, user_id=user.id,
                                  body=" ".join(args))
            bot.sendMessage(chat_id=message.chat_id, text="Thesis added!")
        else:
            print("ALREADY HAVE THAT THESIS")
            bot.sendMessage(chat_id=message.chat_id, text="This thesis already exists!")
        print("DONE")


def stopAll(signum=None, frame=None):
    print("STOPPING")
    dbconfig.close()


TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise EnvironmentError("TOKEN not found")
updater = Updater(TOKEN, user_sig_handler=stopAll)
# Get the dispatcher to register handlers
dp = updater.dispatcher
# Add handlers for Telegram messages
help_handler = CommandHandler('help', c_help)
dp.add_handler(help_handler)
thesis_handler = CommandHandler('thesis', thesis, pass_args=True)
dp.add_handler(thesis_handler)
last30minsTheses_handler = CommandHandler('last30minsTheses', last30minsTheses)
dp.add_handler(last30minsTheses_handler)
last5hoursTheses_handler = CommandHandler('last5hoursTheses', last5hoursTheses)
dp.add_handler(last5hoursTheses_handler)
updater.start_polling()
updater.idle()
