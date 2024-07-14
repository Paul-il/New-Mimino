# bot/telegram_bot/keyboard.py
from telegram import KeyboardButton, ReplyKeyboardMarkup

def main_keyboard():
    keyboard = [
        [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
        [KeyboardButton("Другие команды")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
