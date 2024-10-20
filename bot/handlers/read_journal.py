import logging
import time

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import db_io
from bot.keyboards import cancel_keyboard, start_keyboard
from ..fsm_states import ReadJournal

logger = logging.getLogger(__name__)

router = Router()


def check_date(date):
    logger.debug(f'Необходимо проверить на соответствие dd mm yy {date}')
    if len(date) != 8:
        logger.debug(f'{date} длиннее 8 символов')
        return False
    for i in date.split('.'):
        if (len(i) not in (1, 2)) or not i.isdigit():
            logger.debug(f'{i} содержит недопустимые символы')
            return False
    return True


def convert_date(date):
    in_data = list(map(int, date.split('.')))
    return int(time.mktime(time.strptime(f'{in_data[2] + 2000}-{in_data[1]}-{in_data[0] + 1} 00:00:00',
                                         '%Y-%m-%d %H:%M:%S')))


@router.callback_query(F.data == 'read')
async def set_period_journal_from(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Необходимо указать стартовую дату "дд.мм.гг"'
                                          '\nили 0 для вывода с самого начала', reply_markup=cancel_keyboard)
    await state.set_state(ReadJournal.period_from)


@router.message(StateFilter(ReadJournal.period_from))
async def set_period_journal_to(message: Message, state: FSMContext):
    if check_date(message.text):
        await state.update_data(period_from=convert_date(message.text) - (24 * 60 * 60))
        await message.answer(text='Необходимо указать конечную дату "дд.мм.гг"'
                                  '\nили 0 для вывода до текущего момента', reply_markup=cancel_keyboard)
    elif message.text == '0':
        await state.update_data(period_from=0)
        await message.answer(text='Необходимо указать конечную дату "дд.мм.гг"'
                                  '\nили 0 для вывода до текущего момента', reply_markup=cancel_keyboard)
    else:
        await message.answer(text='Необходимо указать стартовую дату "дд.мм.гг"'
                                  '\nили 0 для вывода с самого начала', reply_markup=cancel_keyboard)
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
        await message.answer(text='Необходимо указать конечную дату "дд.мм.гг"'
                                  '\nили 0 для вывода до текущего момента', reply_markup=cancel_keyboard)
        return
    logger.debug(await state.get_data())
    data = await state.get_data()
    rows = db_io.get_list_from_journal(message.from_user.id, data.get('period_from'), data.get('period_to'))
    await message.answer('За данный период получены следующие записи:')
    for row in rows:
        location = ', '.join(row[3])
        time_local = time.localtime(row[0])
        answer = (f'В {time.strftime('%H:%M %d.%m.%Y г.', time_local)} была добавлена следующая запись:\n'
                  f'Почувствовал: {row[1]}\n'
                  f'В виде: {row[2]}\n'
                  f'В районе: {location}\n'
                  f'По уровню: {row[4]}.')
        if row[5] != '':
            answer += f'\nТак же был оставлен комментарий "{row[5]}"'
        logger.debug(answer)
        await message.answer(answer)
    await message.answer(text='Записи по запросу выведены.\n Что делаем дальше?', reply_markup=start_keyboard)
    await state.clear()
