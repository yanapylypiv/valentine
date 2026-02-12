from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    group_name = State()


class Valentine(StatesGroup):
    recipient = State()
    message = State()
