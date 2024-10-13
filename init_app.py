import os
import sqlite3
import logging
import dotenv


logger = logging.getLogger(__name__)
dotenv.load_dotenv('configs/.env')


def init_app():
    admin_id = os.getenv('TELEGRAM_ID')
    if not os.path.isfile('database/appdatabase.db'):
        logging.error('Database not found')
        if not os.path.exists('database'):
            logging.error('Path to database not found')
            os.mkdir('database')
            logging.info('Path to database created')
        with sqlite3.connect('database/appdatabase.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                            user_name TEXT NOT NULL,
                            user_telegram_id INTEGER NOT NULL);
                            ''')

            cursor.execute('''CREATE TABLE journal (
                            row_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            feeling_id INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            row_time TIMESTAMP NOT NULL,
                            comment TEXT
                             );''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS feelings (
                            feeling_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            feeling_name TEXT NOT NULL);''')

            cursor.execute('''INSERT INTO feelings (feeling_name)
                            VALUES ('Болей нет');
                            ''')

            logging.info('Database created')
    with sqlite3.connect('database/appdatabase.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
        SELECT user_telegram_id
        FROM users
        WHERE user_telegram_id = {admin_id}
        ''')
        if cursor.fetchone() is None:
            cursor.execute(f'''
            INSERT INTO users (user_name, user_telegram_id)
            VALUES ('admin', {admin_id})
            ''')
            logging.info('Admin user row added into database')

