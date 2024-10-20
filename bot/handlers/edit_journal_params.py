import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

import db_io
from bot.fsm_states import EditParams
from bot.keyboards import choice_params_for_editing_keyboard, cancel_keyboard, type_editing_keyboard, start_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'edit_params')
async def choice_params_for_editing(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Что редактируем?', reply_markup=choice_params_for_editing_keyboard)
    await state.set_state(EditParams.choised_param)


@router.callback_query(F.data.in_({'edit_category_feeling', 'edit_feeling', 'edit_location_feeling'}),
                       StateFilter(EditParams.choised_param))
async def type_edit_params(call: CallbackQuery, state: FSMContext):
    await state.update_data(param=call.data)
    await call.message.edit_text(text='Что надо сделать?', reply_markup=type_editing_keyboard)
    await state.set_state(EditParams.choised_type)


@router.callback_query(F.data == 'add', StateFilter(EditParams.choised_type))
async def add_edit_params(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Введите имя для новой записи', reply_markup=cancel_keyboard)
    await state.set_state(EditParams.wait_add_param)


@router.message(StateFilter(EditParams.wait_add_param))
async def add_new_param(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = int(message.from_user.id)
    row_data = db_io.RowData()
    match data['param']:
        case 'edit_category_feeling':
            row_data.category_feeling_name = message.text
            db_io.add_new_type_feeling_category(user_id, row_data)
        case 'edit_feeling':
            row_data.feeling_name = message.text
            db_io.add_new_type_feeling(user_id, row_data)
        case 'edit_location_feeling':
            row_data.feeling_location_name = message.text
            db_io.add_new_type_feeling_location(user_id, row_data)
    await state.set_state(default_state)
    await message.answer(text='Параметр добавлен\n Что делаем дальше?', reply_markup=start_keyboard)


@router.callback_query(F.data == 'rename', StateFilter(EditParams.choised_type))
async def rename_params(call: CallbackQuery, state: FSMContext):
    await call.answer(text='Пока не работает', show_alert=True)
    await call.message.edit_text(text='Что делаем дальше?', reply_markup=start_keyboard)
    await state.set_state(default_state)
