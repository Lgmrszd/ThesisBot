import os.path
import datetime
import dbconfig
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='[%(asctime)s][%(levelname)s]:%(message)s', level=logging.DEBUG, datefmt='%d.%m.%Y %H:%M:%S')


def gen_kb():
    m30 = InlineKeyboardButton("30 minutes", callback_data="lt:00:30:00")
    h1 = InlineKeyboardButton("1 hour", callback_data="lt:01:00:00")
    h5 = InlineKeyboardButton("5 hours", callback_data="lt:05:00:00")
    h10 = InlineKeyboardButton("10 hours", callback_data="lt:10:00:00")
    h24 = InlineKeyboardButton("1 day", callback_data="lt:24:59:00")
    d = InlineKeyboardButton("DELET THIS", callback_data="DELETE")
    kb = InlineKeyboardMarkup(inline_keyboard=[[m30, h1, h5, h10, h24], [d]])
    return kb


def thesisToText(text, stime):
    return ("\n"
            "✅ %s \n"
            "~ published at %s \n"
            "\n") % (text, stime)


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
        st = thesisToText(tbody, stime)
        str_theses.append(st)
    bot.sendMessage(chat_id=message.chat_id,
                    text="Theses in last 30 minutes:\n\n" + "\n".join(str_theses))


def last5hoursTheses(bot, update):
    message = update.message
    theses = dbconfig.getLast5hoursTheses(message.chat_id)
    str_theses = []
    for t in theses:
        stime = fromUTCtoTZ(t['creation_time']).strftime('%m.%d %H:%M:%S')
        tbody = t['body']
        st = thesisToText(tbody, stime)
        str_theses.append(st)
    bot.sendMessage(chat_id=message.chat_id,
                    text="Theses in last 5 hours:\n\n" + "\n".join(str_theses))


def lastThesesByIntervalToText(chat_id, dt):
    theses = dbconfig.getLastThesesByTime(chat_id, dt)
    str_theses = []
    if theses:
        for t in theses:
            stime = fromUTCtoTZ(t['creation_time']).strftime('%m.%d %H:%M:%S')
            tbody = t['body']
            st = thesisToText(tbody, stime)
            str_theses.append(st)
        str_theses_r = "—— ‼️ Theses in last %s ‼️ ——\n" % dt + "\n".join(str_theses) + "—— end of theses ——"
        return str_theses_r
    else:
        return "No theses available in interval %s" % dt


def lastThesesByInterval(bot, update):
    dt = "00:30:00"
    message = update.message
    str_theses = lastThesesByIntervalToText(message.chat_id, dt)
    bot.sendMessage(chat_id=message.chat_id,
                    reply_markup=gen_kb(),
                    text=str_theses)


def onCallback(bot, update):
    print("INTEST")
    cb = update.callback_query
    print(cb.data)
    m_id = cb.message.message_id
    c_id = cb.message.chat.id
    print(m_id, c_id)
    if cb.data == "DELETE":
        bot.deleteMessage(chat_id=c_id, message_id=m_id)
    else:
        dt = cb.data[3:]
        message = cb.message
        str_theses = lastThesesByIntervalToText(message.chat_id, dt)
        bot.editMessageText(chat_id=c_id, message_id=m_id, text=str_theses, reply_markup=gen_kb())


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
lastThesesByInterval_handler = CommandHandler('lt', lastThesesByInterval)
dp.add_handler(lastThesesByInterval_handler)
cb_handler = CallbackQueryHandler(onCallback)
dp.add_handler(cb_handler)
updater.start_polling()
updater.idle()
