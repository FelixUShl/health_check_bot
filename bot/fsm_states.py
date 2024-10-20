from aiogram.fsm.state import State, StatesGroup


class WriteJournal(StatesGroup):
    selected_category = State()
    start_selecting_location = State()
    selecting_location = State()
    selected_location = State()
    selected_feeling = State()
    selected_level = State()
    add_comment = State()


class ReadJournal(StatesGroup):
    period_from = State()  # Сотсояние выставляемое для ожидания ввода начальной даты
    period_to = State()  # Сотсояние когда период выставлен


class EditParams(StatesGroup):
    choised_param = State()
    choised_type = State()
    wait_add_param = State()

