import config
import dbconnect
import logging
from thesisbot import ThesisBot


def main():
    logging.basicConfig(format='[%(asctime)s][%(levelname)s]:%(message)s', level=logging.WARNING, datefmt='%d.%m.%Y %H:%M:%S')

    token = config.get_token()
    db_url = config.get_db_url()

    bot_db = dbconnect.BotDB(db_url)

    thesisbot = ThesisBot(token, bot_db)
    thesisbot.run()


if __name__ == "__main__":
    main()
