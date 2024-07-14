import logging
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
from bot.telegram_bot.utils import get_data, get_tips, get_table_data, get_unavailable_products, get_delivery_data, get_bookings, choose_date

logger = logging.getLogger(__name__)

async def start(update, context):
    keyboard = [
        [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
        [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
        [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
        [KeyboardButton("Другие команды")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Выберите команду:', reply_markup=reply_markup)

async def menu(update, context):
    keyboard = [
        [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
        [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
        [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
        [KeyboardButton("Другие команды")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Выберите команду:', reply_markup=reply_markup)

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("choose_date", choose_date))
    application.add_handler(MessageHandler(filters.Regex("^(Меню)$"), menu))
    application.add_handler(MessageHandler(filters.Regex("^(Сводка)$"), get_data))
    application.add_handler(MessageHandler(filters.Regex("^(Чаевые официантов)$"), get_tips))
    application.add_handler(MessageHandler(filters.Regex("^(Открытые столы)$"), get_table_data))
    application.add_handler(MessageHandler(filters.Regex("^(Недоступные продукты)$"), get_unavailable_products))
    application.add_handler(MessageHandler(filters.Regex("^(Сводка по доставке)$"), get_delivery_data))
    application.add_handler(MessageHandler(filters.Regex("^(Забронированные столы)$"), get_bookings))
    application.add_handler(MessageHandler(filters.Regex(r'^\d{4}-\d{2}-\d{2}$'), get_bookings))  # Регулярное выражение для выбора даты
