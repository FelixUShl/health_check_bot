import logging

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command('cancel'), ~StateFilter(default_state))
async def cansel_input(message: Message, state: FSMContext):
    await message.answer('Ожидание ввода отменено')
    logger.info(f'Сброс состояния до default_state')
    await state.clear()


@router.message(Command('cancel'), StateFilter(default_state))
async def cansel_input(message: Message):
    await message.answer('Нечего сбрасывать. Бот ждет команды')
    logger.info(f'Попытка сброса до состояния default_state, хотя и так в нем')
