import os
import urllib.parse as urlparse
from pg import DB
import time
import datetime

urlparse.uses_netloc.append("postgres")
if os.environ.get("DATABASE_URL"):
    url = urlparse.urlparse(os.environ.get("DATABASE_URL"))
else:
    raise EnvironmentError("DATABASE_URL not found")

db = DB(
    dbname=url.path[1:],
    user=url.username,
    passwd=url.password,
    host=url.hostname,
    port=url.port
)

def insertThesis(init_id, chat_id, user_id, body):
    global db
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print("inserting thesis")
    print(init_id, chat_id, user_id, body, timestamp)
    db.insert("theses", row={"init_id":init_id, "chat_id":chat_id, "user_id":user_id, "body":body, "time":timestamp})
    print("done")
    db.commit()

def insertUser(user_id, username, first_name, last_name):
    global db
    ts = time.time()
    row = {"user_id":user_id}
    if username:
        row["username"] = username
    if first_name:
        row["first_name"] = first_name
    if last_name:
        row["last_name"] = last_name
    db.insert('users', row=row)
    db.commit()

def getUser(user_id):
    global db
    query = db.query("SELECT * FROM users WHERE user_id = %d"%user_id)
    dictres = query.dictresult()
    if len(dictres) == 0:
        return False
    else:
        return dictres[0]

def close():
    db.close()
