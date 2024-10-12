import os
from aiogram import Bot, Dispatcher, F
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import db_io
import dotenv
import time

logger = logging.getLogger(__name__)
memory = MemoryStorage()
dotenv.load_dotenv('configs/.env')
approved_tokens = db_io.get_list_users_telegram_tokens()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(memory=memory)
admin_id = os.getenv('TELEGRAM_ID')


class States(StatesGroup):
    get_feeling = State()
    feeling_row_id = None
    get_feeling_comment = State()
    get_new_feeling_type = State()
    set_period_journal = State()


@dp.message(~F.from_user.id.in_(approved_tokens))
async def not_approved_user(message: Message):
    await message.answer('Вы не авторизованы!')
    await bot.send_message(admin_id, f"Попытка взаимодействия\n"
                                     f"Имя: {message.from_user.first_name},\n"
                                     f"Никнэйм: {message.from_user.username},\n"
                                     f"UserID: {message.from_user.id}")
    await bot.send_message(admin_id, message.text)
    logger.info(f'Попытка взаимодействия неавторизованным пользователем {message.from_user.id}, {message.message_id}')


@dp.message(Command('start'), StateFilter(default_state))
async def start(message: Message):
    await message.answer('Привет!\n/set_feeling\n/get_journal')


@dp.message(Command('set_feeling'), StateFilter(default_state))
async def set_feeling(message: Message, state: FSMContext):
    feelings = db_io.get_list_feelings()
    await message.answer('Выбери подходящее состояние:')
    for feeling in feelings:
        await message.answer(feeling)
    await state.set_state(States.get_feeling)


@dp.message(StateFilter(States.get_feeling))
async def set_row_journal(message: Message, state: FSMContext):
    States.feeling_row_id = db_io.add_new_row_journal(message.from_user.id, message.text)
    await message.answer('Введи комментарий к записи, или введи /cansel')
    await state.set_state(States.get_feeling_comment)


@dp.message(StateFilter(States.get_feeling_comment))
async def set_comment_to_journal(message: Message, state: FSMContext):
    if message.text == '/cansel':
        await message.answer('Без комментариев')
        await state.set_state(default_state)
    else:
        db_io.add_comment_to_row_journal(message.text, States.feeling_row_id)
        await message.answer('Комментарий успешно добавлен')
        await state.set_state(default_state)


@dp.message(Command('get_journal'), StateFilter(default_state))
async def start(message: Message, state: FSMContext):
    await message.answer('Укажи за какой период')
    await state.set_state(States.set_period_journal)


@dp.message(StateFilter(States.set_period_journal))
async def start(message: Message, state: FSMContext):
    rows = db_io.get_list_from_journal(message.from_user.id)
    await message.answer('За данный период получены следующие записи:')
    for row in rows:
        time_local = time.localtime(row[0])
        answer = f'{time.strftime('%d.%m.%Y г. %H:%M', time_local)}'
        answer += f', {row[1]}'
        if row[2] != '':
            answer += f',\nКомментарий: {row[2]}'
        await message.answer(answer)
    await state.set_state(States.set_period_journal)


@dp.message(Command('cansel'))
async def start(message: Message, state: FSMContext):
    await message.answer('Ожидание ввода отменено')
    await state.set_state(default_state)

async def start_():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)
