import logging

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

import db_io
from ..fsm_states import WriteJournal

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("new_row"), StateFilter(default_state))
async def new_row(message: Message, state: FSMContext):
    feelings = db_io.get_list_feelings()
    await message.answer('Выбери подходящее состояние, или введи /cancel:')
    for feeling in feelings:
        await message.answer(feeling)
    await state.set_state(WriteJournal.selected_feeling)


@router.message(F.text.in_(db_io.get_list_feelings()), StateFilter(WriteJournal.selected_feeling))
async def select_feeling(message: Message, state: FSMContext):
    logger.info(f'Для записи в журнал передано ощущение {message.text}')
    await state.update_data(row_id=db_io.add_new_row_journal(message.from_user.id, message.text))
    await message.answer('Введи комментарий к записи, или введи /cansel')
    await state.set_state(WriteJournal.set_comment)


@router.message(StateFilter(WriteJournal.set_comment))
async def select_feeling(message: Message, state: FSMContext):
    data = await state.get_data()
    row_id = data['row_id']
    db_io.add_comment_to_row_journal(message.text, row_id)
    logger.info(f'Комментарий успешно добавлен')
    await message.answer('Комментарий успешно добавлен')
    await state.clear()
    logger.info(f'Сброс состояния до default_state')
