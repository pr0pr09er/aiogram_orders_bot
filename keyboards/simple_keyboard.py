from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str]) -> ReplyKeyboardBuilder:
    keyboard = ReplyKeyboardBuilder()
    for elem in range(len(items)):
        keyboard.add(KeyboardButton(text=items[elem]))
    keyboard.adjust(1)

    return keyboard
