from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message
import logging

import db_io
from bot.init_bot import bot, admin_id

logger = logging.getLogger(__name__)

router = Router()


@router.message(~F.from_user.id.in_(db_io.get_list_users_telegram_tokens()))
async def not_approved_user(message: Message):
    await message.answer('Вы не авторизованы!')
    await bot.send_message(admin_id, f"Попытка взаимодействия\n"
                                     f"Имя: {message.from_user.first_name},\n"
                                     f"Никнэйм: {message.from_user.username},\n"
                                     f"UserID: {message.from_user.id}")
    await bot.send_message(admin_id, message.text)
    logger.info(f'Попытка взаимодействия неавторизованным пользователем {message.from_user.id}, {message.message_id}')


@router.message(Command('start'), StateFilter(default_state))
async def start(message: Message):
    await message.answer('Привет!\n/new_row\n/read_journal')
