import logging
import time

from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

import db_io
from ..fsm_states import ReadJournal

logger = logging.getLogger(__name__)

router = Router()


def check_date(date):
    logger.debug(f'Необходимо проверить на соответствие dd mm yy {date}')
    if len(date) != 8:
        logger.debug(f'{date} длиннее 8 символов')
        return False
    for i in date.split():
        if len(i) != 2 or not i.isdigit():
            logger.debug(f'{i} содержит недопустимые символы')
            return False
    return True


def convert_date(date):
    in_data = list(map(int, date.split()))
    return int(time.mktime(time.strptime(f'{in_data[2] + 2000}-{in_data[1]}-{in_data[0] + 1} 03:00:00',
                                         '%Y-%m-%d %H:%M:%S')))


@router.message(Command('read_journal'), StateFilter(default_state))
async def set_period_journal_from(message: Message, state: FSMContext):
    await message.answer('Необходимо указать дату "дд мм гг" или 0 для вывода с самого начала'
                         '\n/cancel для отмены')
    await state.set_state(ReadJournal.period_from)


@router.message(StateFilter(ReadJournal.period_from))
async def set_period_journal_to(message: Message, state: FSMContext):
    if check_date(message.text):
        await state.update_data(period_from=convert_date(message.text) - (24 * 60 * 60))
        await message.answer('Необходимо указать конечную дату дд:мм:гг\nили 0 если по сейчас\n/cancel для отмены')
    elif message.text == '0':
        await state.update_data(period_from=0)
    else:
        await message.answer('Необходимо указать стартовую дату "дд мм гг"\nили 0 для вывода с самого начала'
                             '\n/cancel для отмены')
        await message.answer('Необходимо указать конечную дату дд:мм:гг\nили 0 если по сейчас\n/cancel для отмены')
        return
    await state.set_state(ReadJournal.period_to)
    logger.debug(await state.get_data())


@router.message(StateFilter(ReadJournal.period_to))
async def set_period_journal(message: Message, state: FSMContext):
    logger.debug(await state.get_data())
    if check_date(message.text):
        await state.update_data(period_to=convert_date(message.text))
    elif message.text == '0':
        await state.update_data(period_to=0)
    else:
        await message.answer('Необходимо указать конечную дату дд:мм:гг\nили 0 если по сейчас\n/cancel для отмены')
        return
    logger.debug(await state.get_data())
    data = await state.get_data()
    rows = db_io.get_list_from_journal(message.from_user.id, data.get('period_from'), data.get('period_to'))
    await message.answer('За данный период получены следующие записи:')
    for row in rows:
        time_local = time.localtime(row[0])
        answer = f'{time.strftime('%d.%m.%Y г. %H:%M', time_local)}'
        answer += f', {row[1]}'
        if row[2] != '':
            answer += f',\nКомментарий: {row[2]}'
        await message.answer(answer)
    await state.clear()
