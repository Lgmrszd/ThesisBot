import os
import urllib.parse as urlparse
from pgdb import connect

urlparse.uses_netloc.append("postgres")
if os.environ.get("DATABASE_URL"):
    url = urlparse.urlparse(os.environ.get("DATABASE_URL"))
else:
    raise EnvironmentError("DATABASE_URL not found")

conn = connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname+":"+str(url.port)
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE theses (
    init_id         int,
    chat_id         int,
    user_id         int,
    body            TEXT,
    time            timestamp
);
""")
conn.commit()
cur.execute("""
CREATE TABLE users (
    user_id         int,
    username        TEXT,
    first_name      TEXT,
    last_name       TEXT
);
""")
conn.commit()
cur.close()
conn.close()
