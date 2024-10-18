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
                            user_telegram_id INTEGER NOT NULL)
                            ''')

            cursor.execute(f'''CREATE TABLE journal
                            (row_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            category_feeling_id INTEGER NOT NULL,
                            feeling_location_id TEXT NOT NULL,
                            feeling_id INTEGER NOT NULL,
                            feeling_level_id INTEGER NOT NULL,
                            row_time TIMESTAMP NOT NULL,
                            comment TEXT);''')

            cursor.execute(f'''CREATE TABLE IF NOT EXISTS feelings_level (
                                feelings_level_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                feelings_level_name TEXT NOT NULL,
                                user_id INTEGER NOT NULL);''')


            cursor.execute(f'''CREATE TABLE IF NOT EXISTS feelings_location (
                                feeling_location_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                feeling_location_name TEXT NOT NULL,
                                user_id INTEGER NOT NULL);''')


            cursor.execute(f'''CREATE TABLE IF NOT EXISTS feelings (
                                feeling_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                feeling_name TEXT NOT NULL,
                                user_id INTEGER NOT NULL);''')

            cursor.execute(f'''CREATE TABLE IF NOT EXISTS categories_feeling (
                                category_feeling_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                category_feeling_name TEXT NOT NULL,
                                user_id INTEGER NOT NULL);''')



            logging.info('Database created')
    with sqlite3.connect('database/appdatabase.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT user_id
                            FROM users
                            WHERE user_telegram_id = ?
                            ''', (admin_id, ))
        if cursor.fetchone() is None:
            print(cursor.fetchone())
            cursor.execute('''
            INSERT INTO users (user_name, user_telegram_id)
            VALUES ('admin', ?)
            ''', (admin_id,))
            logging.info('Admin user row added into database')
            cursor.execute('''
                    SELECT user_id
                    FROM users
                    WHERE user_telegram_id = ?
                            ''', (admin_id, ))
            user_id = cursor.fetchone()[0]
            cursor.execute(f'''INSERT INTO categories_feeling (category_feeling_name, user_id)
                        VALUES ('Болей нет', ?)
                            ''', (user_id, ))

if __name__ == '__main__':
    init_app()