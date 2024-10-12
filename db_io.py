import logging
import sqlite3
import time

logger = logging.getLogger(__name__)


def get_user_id(telegram_user_id):
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_telegram_id = ?", (telegram_user_id,))
        return cursor.fetchone()[0]


def add_new_row_journal(telegram_user_id, feeling_name):
    user_id = get_user_id(telegram_user_id)
    row_time = int(time.time())
    logger.debug(row_time)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT feeling_id FROM feelings WHERE feeling_name = ?", (feeling_name,))
        feeling_id = cursor.fetchone()[0]
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''INSERT 
                                INTO
                                    journal
                                    (feeling_id, user_id, row_time)                             
                                VALUES
                                    (?, ?, ?)''', (feeling_id, user_id, row_time))
        cursor.execute('''SELECT row_id FROM journal WHERE row_time = ?''', (row_time,))
        logger.info(f'Добавлена новая запись в журнал пользователя {telegram_user_id}')
        return cursor.fetchone()[0]


def add_new_type_feeling(new_feeling_name):
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''UPDATE
                                    INSERT 
                                    INTO
                                        feelings
                                        (feeling_name)                                     
                                    VALUES
                                        (?)''', (new_feeling_name,))
        logger.info(f'Добавлен новый тип ощущения {new_feeling_name}')


def add_comment_to_row_journal(comment, row_id):
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''UPDATE
                                    journal                                 
                                SET
                                    comment = ?                                  
                                WHERE
                                    row_id = ?''', (comment, row_id))


def get_list_from_journal(telegram_user_id, time_from=0, time_to='now'):
    if time_to == 'now':
        time_to = int(time.time())
    user_id = get_user_id(telegram_user_id)
    res = list()
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT
                                    row_time,
                                    feeling_name,
                                    IFNULL(comment,
                                    '')                             
                                FROM
                                    journal                             
                                JOIN
                                    feelings 
                                        ON journal.feeling_id = feelings.feeling_id                             
                                WHERE
                                    row_time BETWEEN ? AND ? 
                                    and user_id = ?''',
                       (time_from, time_to, user_id))
    logger.info(f'Выполнен запрос к получению записей журнала пользователя {telegram_user_id} '
                f'с {time_from} по {time_to} глобальную секунду')
    return cursor.fetchall()


def get_list_users_telegram_tokens():
    with sqlite3.connect('database/appdatabase.db') as con:
        result = list()
        cursor = con.cursor()
        cursor.execute('''
                            SELECT
                                user_telegram_id 
                            FROM
                                users
                        ''')
        for row in cursor.fetchall():
            result.append(row[0])
    return result

def get_list_feelings():
    with sqlite3.connect('database/appdatabase.db') as con:
        result = list()
        cursor = con.cursor()
        cursor.execute('''
                       SELECT feeling_name
                       FROM feelings
                       ''')
        for row in cursor.fetchall():
            result.append(row[0])
    return result
