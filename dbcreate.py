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

# cur.execute("""
# CREATE TABLE users (
#     user_id         bigint PRIMARY KEY,
#     username        TEXT,
#     first_name      TEXT,
#     last_name       TEXT
# );
# """)

cur.execute("""
-- auto-generated definition
CREATE TABLE users
(
  user_id    BIGINT NOT NULL
    CONSTRAINT users_pkey
    PRIMARY KEY,
  username   TEXT,
  first_name TEXT,
  last_name  TEXT
);
""")
conn.commit()

# cur.execute("""
# CREATE TABLE theses (
#     init_id         bigint,
#     chat_id         bigint,
#     user_id         bigint REFERENCES users (user_id),
#     body            TEXT UNIQUE,
#     creation_time   timestamp with time zone DEFAULT current_timestamp,
#     PRIMARY KEY (init_id, chat_id)
# );
# """)

cur.execute("""
-- auto-generated definition
CREATE TABLE theses
(
  init_id       BIGINT NOT NULL,
  chat_id       BIGINT NOT NULL,
  user_id       BIGINT
    CONSTRAINT theses_user_id_fkey
    REFERENCES users,
  body          TEXT UNIQUE,
  creation_time TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
  CONSTRAINT theses_pkey
  PRIMARY KEY (init_id, chat_id)
);
""")

conn.commit()

cur.execute("""
-- auto-generated definition
CREATE TABLE bot_messages
(
  chat_id    BIGINT,
  message_id BIGINT,
  owner_id   BIGINT
);
""")

conn.commit()
cur.close()
conn.close()
