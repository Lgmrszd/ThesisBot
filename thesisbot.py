from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime


def c_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="""Supported commands:
/help - Show this
/thesis thesis text - add new thesis
/lt - get latest theses""")


def fromUTCtoTZ(dt):
    tz = datetime.timezone(datetime.timedelta(hours=3))
    return dt.astimezone(tz)


def thesisToText(text, stime, t_id):
    return ("\n"
            "✅ %s \n"
            "~ published at %s, id %d \n"
            "\n") % (text, stime, t_id)

def gen_kb():
    m30 = InlineKeyboardButton("30 minutes", callback_data="lt:00:30:00")
    h1 = InlineKeyboardButton("1 hour", callback_data="lt:01:00:00")
    h5 = InlineKeyboardButton("5 hours", callback_data="lt:05:00:00")
    h10 = InlineKeyboardButton("10 hours", callback_data="lt:10:00:00")
    h24 = InlineKeyboardButton("1 day", callback_data="lt:24:00:00")
    d = InlineKeyboardButton("DELET THIS", callback_data="DELETE")
    kb = InlineKeyboardMarkup(inline_keyboard=[[m30, h1, h5, h10, h24], [d]])
    return kb


class ThesisBot:
    def __init__(self, token, bot_db):
        self.__token = token
        self.__bot_db = bot_db
        self.__updater = Updater(token, user_sig_handler=self.stop_all)
        self.__dp = self.__updater.dispatcher
        self.add_command_handler("help", c_help)
        self.add_command_handler("thesis", self.new_thesis, pass_args=True)
        self.add_command_handler("lt", self.lastThesesByInterval)
        self.add_command_handler("id_thesis", self.thesisById, pass_args=True)
        self.add_callback_handler(self.on_callback)

    def test(self, bot, update):
        print("TEST", self, bot, update)

    def add_command_handler(self, command, callback, pass_args=False):
        ch = CommandHandler(command, callback, pass_args=pass_args)
        self.__dp.add_handler(ch)

    def add_callback_handler(self, callback):
        ch = CallbackQueryHandler(callback)
        self.__dp.add_handler(ch)

    def stop_all(self, signum, frame):
        print("STOPPING, signal:", signum)
        self.__bot_db.close()

    def run(self):
        self.__updater.start_polling()
        self.__updater.idle()

    # ----


    def lastThesesByIntervalToText(self, chat_id, dt):
        theses = self.__bot_db.getLastThesesByTime(chat_id, dt)
        str_theses = []
        if theses:
            for t in theses:
                print(t)
                stime = fromUTCtoTZ(t['creation_time']).strftime('%m.%d %H:%M:%S')
                tbody = t['body']
                t_id = t['init_id']
                st = thesisToText(tbody, stime, t_id)
                str_theses.append(st)
            str_theses_r = "—— ‼️ Theses in last %s ‼️ ——\n" % dt + "\n".join(str_theses) + "—— end of theses ——"
            return str_theses_r
        else:
            return "No theses available in interval %s" % dt


    def lastThesesByInterval(self, bot, update):
        dt = "00:30:00"
        message = update.message
        str_theses = self.lastThesesByIntervalToText(message.chat_id, dt)
        b_msg = bot.sendMessage(chat_id=message.chat_id,
                        reply_markup=gen_kb(),
                        text=str_theses)
        user = update.message.from_user
        self.__bot_db.insertBotMessage(chat_id=message.chat_id, message_id=b_msg.message_id, owner_id=user.id)


    def thesisById(self, bot, update, args):
        message = update.message
        if len(args) == 1:
            thesis = self.__bot_db.getThesisByIds(int(args[0]), message.chat_id)
            print(thesis)
            if thesis:
                stime = fromUTCtoTZ(thesis['creation_time']).strftime('%m.%d %H:%M:%S')
                tbody = thesis['body']
                t_id = thesis['init_id']
                str_thesis = thesisToText(tbody, stime, t_id)
                bot.sendMessage(chat_id=message.chat_id,
                                text=str_thesis,
                                reply_to_message_id = int(args[0]))
            else:
                bot.sendMessage(chat_id=message.chat_id,
                                text="There is no thesis with this id")

        else:
            bot.sendMessage(chat_id=message.chat_id,
                            text="wrong argument")


    def on_callback(self, bot, update):
        print("INTEST")
        cb = update.callback_query
        print(cb.data)
        m_id = cb.message.message_id
        c_id = cb.message.chat.id
        print(m_id, c_id)
        b_msg = self.__bot_db.getBotMessage(c_id, m_id)
        owner_id = b_msg["owner_id"]
        if owner_id == cb.from_user.id:
            if cb.data == "DELETE":
                bot.deleteMessage(chat_id=c_id, message_id=m_id)
            else:
                dt = cb.data[3:]
                message = cb.message
                str_theses = self.lastThesesByIntervalToText(message.chat_id, dt)
                bot.editMessageText(chat_id=c_id, message_id=m_id, text=str_theses, reply_markup=gen_kb())
                cb.answer


    def new_thesis(self, bot, update, args=""):
        print(self, bot, update, args)
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
            db_user = self.__bot_db.getUserById(user.id)
            if not db_user:
                print("ADDING USER")
                self.__bot_db.insertUser(user_id=user.id, username=user.username, first_name=user.first_name,
                                    last_name=user.last_name)
            else:
                print("ALREADY HAVE THAT USER")
            print("INSERTING THESIS")
            db_thesis = self.__bot_db.getThesisByBody(" ".join(args))
            if not db_thesis:
                print("ADDING THESIS")
                self.__bot_db.insertThesis(init_id=message.message_id, chat_id=message.chat.id, user_id=user.id,
                                      body=" ".join(args))
                b_msg = bot.sendMessage(chat_id=message.chat_id, text="Thesis added!")
                self.__bot_db.insertBotMessage(chat_id=message.chat_id, message_id=b_msg.message_id, owner_id=user.id)
            else:
                print("ALREADY HAVE THAT THESIS")
                bot.sendMessage(chat_id=message.chat_id, text="This thesis already exists!")
            print("DONE")

    def new_thesis(self, bot, update, args):
        print(self, bot, update, args)
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
            db_user = self.__bot_db.getUserById(user.id)
            if not db_user:
                print("ADDING USER")
                self.__bot_db.insertUser(user_id=user.id, username=user.username, first_name=user.first_name,
                                    last_name=user.last_name)
            else:
                print("ALREADY HAVE THAT USER")
            print("INSERTING THESIS")
            db_thesis = self.__bot_db.getThesisByBody(" ".join(args))
            if not db_thesis:
                print("ADDING THESIS")
                self.__bot_db.insertThesis(init_id=message.message_id, chat_id=message.chat.id, user_id=user.id,
                                      body=" ".join(args))
                b_msg = bot.sendMessage(chat_id=message.chat_id, text="Thesis added!")
                self.__bot_db.insertBotMessage(chat_id=message.chat_id, message_id=b_msg.message_id, owner_id=user.id)
            else:
                print("ALREADY HAVE THAT THESIS")
                bot.sendMessage(chat_id=message.chat_id, text="This thesis already exists!")
            print("DONE")
