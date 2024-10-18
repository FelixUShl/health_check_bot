import logging
import sqlite3
import time
from types import NoneType


logger = logging.getLogger(__name__)

class RowData:
    def __init__(self):
        self.category_feeling_id: int|None = None
        self.feeling_location_id: int|None = None
        self.feeling_id: int|None = None
        self.feeling_level_id: int|None = None
        self.row_time: int|None = None
        self.comment: int|None = None
        self.feeling_name: str|None = None
        self.category_feeling_name: str|None = None
        self.user_id: int|None = None
        self.feeling_location_name: str|None = None

def add_new_row_journal(telegram_user_id: int, new_data: RowData):
    new_data.user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''INSERT INTO journal (user_id,
                                                   category_feeling_id,
                                                   feeling_location_id, 
                                                   feeling_id,
                                                   feeling_level_id, 
                                                   row_time, 
                                                   comment)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (new_data.user_id,
                                        new_data.category_feeling_id,
                                        new_data.feeling_location_id,
                                        new_data.feeling_id,
                                        new_data.feeling_level_id,
                                        new_data.row_time,
                                        new_data.comment
                                      ))


def get_user_id(telegram_user_id):
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_telegram_id = ?", (telegram_user_id,))
        res = cursor.fetchone()
        if isinstance(res, NoneType):
            return None
        return res[0]


def add_new_type_feeling(telegram_user_id, new_data: RowData):
    new_data.user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT feeling_id FROM feelings WHERE feeling_name = ? and user_id = ?
                       ''', (new_data.feeling_name, new_data.user_id,))
        if isinstance(cursor.fetchone(), NoneType):
            cursor.execute('''INSERT INTO feelings (feeling_name, user_id) VALUES (?, ?)''',
                           (new_data.feeling_name, new_data.user_id))
            return cursor.lastrowid
        return None


def add_new_type_feeling_category(telegram_user_id, new_data: RowData):
    new_data.user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT category_feeling_id FROM categories_feeling WHERE category_feeling_name = ? and user_id = ?
                       ''', (new_data.category_feeling_name, new_data.user_id))
        if isinstance(cursor.fetchone(), NoneType):
            cursor.execute('''INSERT INTO categories_feeling (category_feeling_name, user_id) VALUES (?, ?)'''
                           , (new_data.category_feeling_name, new_data.user_id))
            return cursor.lastrowid
        return None


def add_new_type_feeling_location(telegram_user_id, new_data: RowData):
    new_data.user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT feeling_location_id FROM feelings_location WHERE feeling_location_name = ? and user_id = ?
                       ''', (new_data.feeling_location_name, new_data.user_id))
        if isinstance(cursor.fetchone(), NoneType):
            cursor.execute('''INSERT INTO feelings_location (feeling_location_name, user_id) VALUES (?, ?)'''
                           , (new_data.feeling_location_name, new_data.user_id))
            return cursor.lastrowid
        return None


def get_list_from_journal(telegram_user_id, time_from=0, time_to=0):
    if time_to == 0:
        time_to = int(time.time())
    user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        cursor = con.cursor()
        cursor.execute('''SELECT row_time,
                                     category_feeling_name,
                                     feeling_name,
                                     feeling_location_id,
                                     feelings_level_name,
                                     IFNULL(comment, '') as comment
                            FROM journal
                            JOIN categories_feeling ON journal.category_feeling_id = categories_feeling.category_feeling_id
                            JOIN feelings ON journal.feeling_id = feelings.feeling_id
                            JOIN feelings_level ON journal.feeling_level_id = feelings_level.feelings_level_id
                            WHERE (row_time BETWEEN ? AND ?) AND journal.user_id = ?''',
                       (time_from, time_to, user_id))
        logger.info(f'Выполнен запрос к получению записей журнала пользователя {telegram_user_id} '
                    f'с {time_from} по {time_to} глобальную секунду')
        rows = cursor.fetchall().copy()  # потому что иначе при следующем запросе данные перезапишутся
        result = list()
        for row in rows:
            location_names = list()
            for location_id in list(map(int, row[3].split(','))):
                cursor.execute('''SELECT feeling_location_name
                                    FROM feelings_location
                                    WHERE feeling_location_id = ? AND feelings_location.user_id = ?''',
                               (location_id, user_id))
                location_names.append(cursor.fetchone()[0])
            row = list(row)
            row[3] = location_names
            result.append(row)
    return result


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


def get_list_feelings(telegram_user_id):
    user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        result = list()
        cursor = con.cursor()
        cursor.execute('''
                       SELECT feeling_name, feeling_id
                       FROM feelings
                       WHERE user_id = ?
                       ''', (user_id,))
        for row in cursor.fetchall():
            result.append(row)
    return result


def get_list_categories_feeling(telegram_user_id):
    user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        result = list()
        cursor = con.cursor()
        cursor.execute('''
                       SELECT category_feeling_name, category_feeling_id
                       FROM categories_feeling
                       WHERE user_id = ?
                       ''', (user_id,))
        for row in cursor.fetchall():
            result.append(row)
    return result


def get_list_feelings_level():
    with sqlite3.connect('database/appdatabase.db') as con:
        result = list()
        cursor = con.cursor()
        cursor.execute('''
                       SELECT feelings_level_name, feelings_level_id
                       FROM feelings_level
                       ''')
        for row in cursor.fetchall():
            result.append(row)
    return result


def get_list_feeling_location(telegram_user_id):
    user_id = get_user_id(telegram_user_id)
    with sqlite3.connect('database/appdatabase.db') as con:
        result = list()
        cursor = con.cursor()
        cursor.execute('''
                       SELECT feeling_location_name, feeling_location_id
                       FROM feelings_location
                       WHERE user_id = ?
                       ''', (user_id,))
        for row in cursor.fetchall():
            result.append(row)
    return result





if __name__ == '__main__':
    row_data = RowData()
    row_data.category_feeling_id = 1
    row_data.feeling_location_id = '1, 3, 2'
    row_data.feeling_id = 11
    row_data.feeling_level_id = 1
    row_data.row_time = int(time.time())
    row_data.comment = None
    row_data.feeling_name = 'Давит'
    row_data.category_feeling_name = 'Невралгия и/или стенокардия'
    row_data.feeling_location_name = 'Спина'

    # print(row_data)
    # add_new_row_journal(987772120, row_data)
    print(get_list_feelings(987772120))
