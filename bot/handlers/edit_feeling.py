import logging

from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

import db_io
from ..fsm_states import NewFeeling

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command('new_feeling'), StateFilter(default_state))
async def new_feeling(message: Message, state: FSMContext):
    await message.answer('Введите название ощущения, или /cancel для отмены')
    await state.set_state(NewFeeling.new_feeling)


@router.message(StateFilter(NewFeeling.new_feeling))
async def new_feeling(message: Message, state: FSMContext):
    if message.text.lower() in (feeling.lower() for feeling in db_io.get_list_feelings()):
        await message.answer('Такое название уже есть')
    else:
        db_io.add_new_type_feeling(message.text)
        await message.answer(f'Ощущение <b>{message.text}</b> добавлено')
    await state.clear()
