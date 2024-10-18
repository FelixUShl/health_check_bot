import logging
import sqlite3
import time
from types import NoneType

logger = logging.getLogger(__name__)



def add_new_row_journal(telegram_user_id: int, row_data: dict):
    row_data['user_id'] = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''INSERT INTO journal (user_id, category_feeling_id, feeling_location_id, feeling_id, feeling_level_id, row_time, comment)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (  row_data['user_id'],
                                            row_data['category_feeling_id'],
                                            row_data['feeling_location_id'],
                                            row_data['feeling_id'],
                                            row_data['feeling_level_id'],
                                            row_data['row_time'],
                                            row_data['comment']
                                        ))


def get_user_id(telegram_user_id):
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_telegram_id = ?", (telegram_user_id,))
        res = cursor.fetchone()
        if isinstance(res, NoneType):
            return None
        return res[0]

def add_new_type_feeling(telegram_user_id, new_data: dict):
    new_data['user_id'] = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT feeling_id FROM feelings WHERE feeling_name = ? and user_id = ?
                       ''', (new_data['feeling_name'], new_data['user_id'], ))
        if isinstance(cursor.fetchone(), NoneType):
            cursor.execute('''INSERT INTO feelings (feeling_name, user_id) VALUES (?, ?)''',
                           (new_data['feeling_name'], new_data['user_id'], ))
            return cursor.lastrowid
        return None





def get_list_from_journal(telegram_user_id, time_from=0, time_to=0):
    if time_to == 0:
        time_to = int(time.time())
    user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT row_time, feeling_name, feeling_location, feeling_lavel, IFNULL(comment,'')                              
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
            result.append(row)
    return result


if __name__ == '__main__':
    row_data = dict()
    row_data['category_feeling_id'] = 1
    row_data['feeling_location_id'] = '1, 3, 2'
    row_data['feeling_id'] = 11
    row_data['feeling_level_id'] = 1
    row_data['row_time']= int(time.time())
    row_data['comment'] = None
    # print(row_data)
    # add_new_row_journal(987772120, row_data)
    print(get_user_id(987772120))