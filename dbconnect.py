import urllib.parse as urlparse
from pg import DB
import time
import datetime


class BotDB:
    def __init__(self, db_url):
        self.__db_url = db_url
        url = urlparse.urlparse(db_url)
        self.__db = DB(
            dbname=url.path[1:],
            user=url.username,
            passwd=url.password,
            host=url.hostname,
            port=url.port
        )

    def insertThesis(self, init_id, chat_id, user_id, body):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("inserting thesis")
        print(init_id, chat_id, user_id, body, timestamp)
        self.__db.insert("theses", row={"init_id": init_id, "chat_id": chat_id, "user_id": user_id, "body": body})
        print("done")
        self.__db.commit()

    def getThesisByIds(self, init_id, chat_id):
        query = self.__db.query("SELECT * FROM theses WHERE init_id = %d AND chat_id = %d;" % (init_id, chat_id))
        dict_res = query.dictresult()
        if len(dict_res) == 0:
            return False
        else:
            return dict_res[0]

    def getThesisByBody(self, body):
        query = self.__db.query("SELECT * FROM theses WHERE body = '%s';" % body)
        dict_res = query.dictresult()
        if len(dict_res) == 0:
            return False
        else:
            return dict_res[0]

    def getLastThesesByTime(self, chat_id, interval):
        query = self.__db.query("SELECT * FROM theses WHERE chat_id = %s AND creation_time > current_timestamp - interval '%s';" % (chat_id, interval))
        dict_res = query.dictresult()
        if len(dict_res) == 0:
            return False
        else:
            return dict_res

    def getTodayTheses(self, chat_id):
        query = self.__db.query("SELECT * FROM theses WHERE chat_id = %s AND creation_time > current_date;" % chat_id)
        dict_res = query.dictresult()
        if len(dict_res) == 0:
            return False
        else:
            return dict_res

    def insertUser(self, user_id, username, first_name, last_name):
        # ts = time.time()
        row = {"user_id":user_id}
        if username:
            row["username"] = username
        if first_name:
            row["first_name"] = first_name
        if last_name:
            row["last_name"] = last_name
        self.__db.insert('users', row=row)
        self.__db.commit()

    def getUserById(self, user_id):
        query = self.__db.query("SELECT * FROM users WHERE user_id = %d;" % user_id)
        dict_res = query.dictresult()
        if len(dict_res) == 0:
            return False
        else:
            return dict_res[0]

    def insertBotMessage(self, chat_id, message_id, owner_id):
        row = {"chat_id": chat_id, "message_id": message_id, "owner_id": owner_id}
        self.__db.insert('bot_messages', row=row)
        self.__db.commit()

    def getBotMessage(self, chat_id, message_id):
        query = self.__db.query("SELECT * FROM bot_messages WHERE chat_id = %d AND message_id = %d;" % (chat_id, message_id))
        dict_res = query.dictresult()
        if len(dict_res) == 0:
            return False
        else:
            return dict_res[0]

    def close(self):
        self.__db.close()
