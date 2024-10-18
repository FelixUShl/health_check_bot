import logging
import asyncio
import dotenv

from configs.log_conf import configure_logging
from init_app import init_app
from bot import start_


def main():
    dotenv.load_dotenv('configs/.env')
    configure_logging()
    logging.getLogger("urllib3").setLevel(logging.ERROR)


if __name__ == '__main__':
    main()
    init_app()
    # import pprint
    # pprint.pprint(db_io.get_list_from_journal(os.getenv('TELEGRAM_ID'), 0, 'now'))
    # db_io.add_comment_to_row_journal('Комментарий1111 для записи в журнал', 1)
    asyncio.run(start_())
