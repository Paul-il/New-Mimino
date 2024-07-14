import logging
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
from bot.telegram_bot.utils import get_data, get_tips, get_table_data, get_unavailable_products

logger = logging.getLogger(__name__)

async def start(update, context):
    keyboard = [
        [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
        [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
        [KeyboardButton("Другие команды")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Выберите команду:', reply_markup=reply_markup)

async def menu(update, context):
    keyboard = [
        [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
        [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
        [KeyboardButton("Другие команды")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Выберите команду:', reply_markup=reply_markup)

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(MessageHandler(filters.Regex("^(Меню)$"), menu))
    application.add_handler(MessageHandler(filters.Regex("^(Сводка)$"), get_data))
    application.add_handler(MessageHandler(filters.Regex("^(Чаевые официантов)$"), get_tips))
    application.add_handler(MessageHandler(filters.Regex("^(Открытые столы)$"), get_table_data))
    application.add_handler(MessageHandler(filters.Regex("^(Недоступные продукты)$"), get_unavailable_products))
