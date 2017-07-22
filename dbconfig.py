import os
import urllib.parse as urlparse
from pgdb import connect

urlparse.uses_netloc.append("postgres")
if os.environ.get("DATABASE_URL"):
    url = urlparse.urlparse(os.environ.get("DATABASE_URL"))
else
    raise EnvironmentError("DATABASE_URL not found")

conn = connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname+":"+str(url.port)
)
