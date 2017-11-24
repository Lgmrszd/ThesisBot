import os.path

mode = 1


def get_token_from_env():
    token = os.environ.get("TOKEN")
    if not token:
        raise EnvironmentError("TOKEN not found")
    return token


def get_db_url_from_env():
    token = os.environ.get("DATABASE_URL")
    if not token:
        raise EnvironmentError("DATABASE_URL not found")
    return token


def get_token_from_file():
    f = open("../thesisbot.cfg", "r")
    token = f.readlines()[1]
    f.close()
    return token.strip("\n")


def get_db_url_from_file():
    f = open("../thesisbot.cfg", "r")
    db_url = f.readlines()[0]
    f.close()
    return db_url.strip("\n")


def get_token():
    if mode == 0:
        return get_token_from_env()
    elif mode == 1:
        return get_token_from_file()


def get_db_url():
    if mode == 0:
        return get_db_url_from_env()
    elif mode == 1:
        return get_db_url_from_file()
