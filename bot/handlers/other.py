import logging

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from bot.keyboards import start_keyboard

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


@router.callback_query(F.data == 'cancel')
async def cansel_input(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text='Операция отменена, возвращаемся на исходную', show_alert=True)
    await callback.message.edit_text('Привет!', reply_markup=start_keyboard)
    logger.info(f'Сброс состояния до default_state')
    await state.clear()