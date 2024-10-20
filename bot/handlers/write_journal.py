import logging
import time

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

import db_io
from bot.keyboards import generate_inline_keyboard, no_keyboard, start_keyboard
from ..fsm_states import WriteJournal

logger = logging.getLogger(__name__)

router = Router()


def convert_data_fow_sql(raw_data: dict) -> db_io.RowData:
    result = db_io.RowData()
    result.category_feeling_id = int(raw_data['category_feeling_id'])
    result.feeling_location_id = ', '.join(list(set(raw_data['feeling_location_id'])))
    result.feeling_id = raw_data['feeling_id']
    result.feeling_level_id = raw_data['feeling_level_id']
    result.row_time = raw_data['row_time']
    result.comment = raw_data.setdefault('comment', None)
    result.user_id = raw_data['user_id']
    return result


def generate_answer_res(result):
    logger.debug(result)
    row = db_io.get_list_from_journal(result['user_id'], result['row_time'], result['row_time'])
    row = row[0]
    location = ', '.join(row[3])
    time_local = time.localtime(row[0])
    answer = (f"В {time.strftime('%H:%M %d.%m.%Y г.', time_local)} была добавлена следующая запись:\n"
              f'Почувствовал: {row[1]}\n'
              f'В виде: {row[2]}\n'
              f'В районе: {location}\n'
              f'По уровню: {row[4]}.')
    if row[5] != '':
        answer += f'\nТак же был оставлен комментарий "{row[5]}"'
    return answer


@router.callback_query(F.data == 'new_entry')
async def select_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Категория текущих ощущений',
                                     reply_markup=generate_inline_keyboard(callback.from_user.id, 'categories_feeling'))
    logger.info('Устанавливаем FSM в состояние "категория выбрана"')
    await state.set_state(WriteJournal.selected_category)
    await state.update_data(row_time=int(time.time()))
    await state.update_data(user_id=int(callback.from_user.id))


@router.callback_query(F.data.startswith('categories_feeling:'), StateFilter(WriteJournal.selected_category))
async def start_select_location(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category_feeling_id=callback.data.split(':')[1])
    await callback.message.edit_text(text='Где ощущается',
                                     reply_markup=generate_inline_keyboard(callback.from_user.id, 'feeling_location'))
    await state.set_state(WriteJournal.start_selecting_location)
    logger.info('Устанавливаем FSM в состояние "Начало выбора мест ощущений"')


@router.callback_query(F.data.startswith('feeling_location:'), StateFilter(WriteJournal.start_selecting_location))
async def selecting_location(callback: CallbackQuery, state: FSMContext):
    locations = list()
    location_id = callback.data.split(':')[1]
    if location_id == 'end':
        await callback.answer(text='Сначала надо выбрать хотя бы одно место ощущений', show_alert=True)
        return None
    locations.append(location_id)
    await callback.answer('Добавлено')
    await state.update_data(feeling_location_id=locations)
    await state.set_state(WriteJournal.selecting_location)
    logger.info('Устанавливаем FSM в состояние "В процессе выбора мест ощущений"')


@router.callback_query(F.data == 'feeling_location:end', StateFilter(WriteJournal.selecting_location))
async def select_location_end(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Что ощущается',
                                     reply_markup=generate_inline_keyboard(callback.from_user.id, 'feelings'))
    locations = await state.get_data()
    locations = locations['feeling_location_id']
    logger.debug(locations)
    # await state.update_data(feeling_location_id=locations)
    logger.info('Устанавливаем FSM в состояние "Места ощущений выбраны"')
    await state.set_state(WriteJournal.selected_location)


@router.callback_query(F.data.startswith('feeling_location:'), StateFilter(WriteJournal.selecting_location))
async def selecting_location_to(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Добавлено')
    locations = await state.get_data()
    locations = locations['feeling_location_id']
    logger.debug(locations)
    locations.append(callback.data.split(':')[1])
    await state.update_data(feeling_location_id=locations)
    logger.info('Добавлено еще одно место ощущений"')


@router.callback_query(F.data.startswith('feelings:'), StateFilter(WriteJournal.selected_location))
async def select_feeling(callback: CallbackQuery, state: FSMContext):
    await state.update_data(feeling_id=callback.data.split(':')[1])
    await callback.message.edit_text(text='Как ощущается',
                                     reply_markup=generate_inline_keyboard(callback.from_user.id, 'feeling_level'))
    await state.set_state(WriteJournal.selected_feeling)
    logger.info('Устанавливаем FSM в состояние "Ощущение выбрано"')


@router.callback_query(F.data.startswith('feeling_level:'), StateFilter(WriteJournal.selected_feeling))
async def select_feeling_level(callback: CallbackQuery, state: FSMContext):
    await state.update_data(feeling_level_id=callback.data.split(':')[1])
    await callback.message.edit_text(text='Написать комментарий',
                                     reply_markup=no_keyboard)
    await state.set_state(WriteJournal.add_comment)
    logger.info('Устанавливаем FSM в состояние "Добавление комментария"')


@router.callback_query(F.data == 'no', StateFilter(WriteJournal.add_comment))
async def add_comment_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text='Действительно, что расписывать то. И так все ясно')
    result = await state.update_data()
    logger.debug(result)
    db_io.add_new_row_journal(callback.from_user.id, convert_data_fow_sql(result))
    await callback.message.answer(generate_answer_res(result))
    await callback.message.answer(text='Что делаем дальше?', reply_markup=start_keyboard)
    await state.set_state(default_state)


@router.message(StateFilter(WriteJournal.add_comment))
async def add_comment(message: Message, state: FSMContext):
    result = await state.update_data()
    result['comment'] = message.text
    logger.debug(result)
    db_io.add_new_row_journal(message.from_user.id, convert_data_fow_sql(result))
    await message.answer(generate_answer_res(result))
    await message.answer(text='Что делаем дальше?', reply_markup=start_keyboard)
    await state.set_state(default_state)
