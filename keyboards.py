from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💌 Написати валентинку")],
            [KeyboardButton(text="📥 Мої валентинки")]
        ],
        resize_keyboard=True
    )
    return keyboard
