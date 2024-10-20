import logging
from faulthandler import cancel_dump_traceback_later

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db_io

logger = logging.getLogger(__name__)

cancel_button = InlineKeyboardButton(text='СБРОС НА СТАРТОВОЕ МЕНЮ', callback_data='cancel')

def generate_inline_keyboard(user_id, type_keyboard):
    user_id = int(user_id)
    buttons = list()
    buttons.append(cancel_button)
    match type_keyboard:
        case 'categories_feeling':
            data = db_io.get_list_categories_feeling(user_id)
        case 'feelings':
            data = db_io.get_list_feelings(user_id)
        case 'feeling_level':
            data = db_io.get_list_feelings_level()
        case 'feeling_location':
            data = db_io.get_list_feeling_location(user_id)
            buttons.append(InlineKeyboardButton(text='ВСЕ ЛОКАЛИЗАЦИИ ВЫБРАНЫ', callback_data=f'feeling_location:end'))
    builder = InlineKeyboardBuilder()

    for category in data:
        buttons.append(InlineKeyboardButton(text=category[0], callback_data=str(f'{type_keyboard}:{category[1]}')))
    builder.row(*buttons, width=3)
    if type_keyboard == 'feeling_location':
        builder.adjust(1, 1, 3)
    else:
        builder.adjust(1, 3)
    return builder.as_markup()


start_keyboard = InlineKeyboardMarkup(inline_keyboard=
                    [[InlineKeyboardButton(text='Новая запись в журнал', callback_data='new_entry')],
                      [InlineKeyboardButton(text='Редактирование параметров', callback_data='edit_params')],
                      [InlineKeyboardButton(text='Посмотреть журнал', callback_data='read')]])


no_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Нет', callback_data='no')]])
cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])


choice_params_for_editing_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                                          [[InlineKeyboardButton(text='Категории ощущений', callback_data='edit_category_feeling')],
                                                          [InlineKeyboardButton(text='Ощущения', callback_data='edit_feeling')],
                                                          [InlineKeyboardButton(text='Локализации', callback_data='edit_location_feeling')],
                                                          [cancel_button]])

type_editing_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                                          [[InlineKeyboardButton(text='Добавить', callback_data='add')],
                                                          [InlineKeyboardButton(text='Переименовать', callback_data='rename')],
                                                          [cancel_button]])