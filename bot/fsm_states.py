from aiogram.fsm.state import State, StatesGroup


class WriteJournal(StatesGroup):
    feeling_row_id = None  # поле нужно для передачи id записи между методами new_row и select_feeling
    selected_feeling = State()  # состояние FSM когда ощущение выбрано
    set_comment = State()  # состояние FSM когда ожидается ввод коментария к записи в журнал


class ReadJournal(StatesGroup):
    period_from = State()  # Сотсояние выставляемое для ожидания ввода начальной даты
    period_to = State()  # Сотсояние когда период выставлен


class NewFeeling(StatesGroup):
    new_feeling = State()
    set_feeling = State()
