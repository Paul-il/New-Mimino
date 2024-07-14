import logging
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def format_datetime(dt_str):
    dt_obj = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt_obj.strftime("%Y-%m-%d %H:%M")

async def get_data(update: Update, context: CallbackContext) -> None:
    url = 'http://127.0.0.1:31337/api/order_summary/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Ответ от сервера: {response.text}")

        data = response.json()

        message = (
            f"Сводка Заказов на Сегодня:\n\n"
            f"Заказы в Ресторане:\n"
            f"Количество: {data['total_orders_today']}\n"
            f"Общая Сумма: {data['total_orders_sum']}₪\n\n"
            f"Самовывоз Заказы:\n"
            f"Количество: {data['total_pickup_orders_today']}\n"
            f"Общая Сумма: {data['total_pickup_orders_sum']}₪\n\n"
            f"Заказы на Доставку:\n"
            f"Количество: {data['total_delivery_orders_today']}\n"
            f"Общая Сумма: {data['total_delivery_orders_sum']}₪\n\n"
            f"Всего:\n"
            f"Количество: {data['total_all_orders_today']}\n"
            f"Общая Сумма: {data['total_all_orders_sum']}₪"
        )

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))

async def get_tips(update: Update, context: CallbackContext) -> None:
    url = 'http://127.0.0.1:31337/api/tip_summary/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Ответ от сервера: {response.text}")

        data = response.json()

        message = "Чаевые официантов за сегодня:\n\n"
        for tip in data:
            message += f"Официант: {tip['first_name']}\n"
            message += f"  Общая сумма чаевых: {tip['total_amount']}₪\n"
            message += "\n"

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))

async def get_table_data(update: Update, context: CallbackContext) -> None:
    url = 'http://127.0.0.1:31337/api/table_summary/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Ответ от сервера: {response.text}")

        data = response.json()

        message = "Открытые столы с продуктами:\n\n"
        for table in data:
            if table['has_products']:
                created_at_formatted = format_datetime(table['created_at'])
                message += (
                    f"Стол №{table['table_id']}:\n"
                    f"Официант: {table['waiter_name']}\n"
                    f"Время начала заказа: {created_at_formatted}\n"
                    f"Количество гостей: {table['num_of_people']}\n"
                    f"Сумма заказа: {table['active_order_total']}₪\n\n"
                )

        if not any(table['has_products'] for table in data):
            message = "Нет открытых столов с продуктами."

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))

async def get_unavailable_products(update: Update, context: CallbackContext) -> None:
    url = 'http://127.0.0.1:31337/api/unavailable_products/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Ответ от сервера: {response.text}")

        data = response.json()

        message = "Недоступные продукты:\n\n"
        for product in data:
            message += f"Продукт: {product['product_name_rus']}\n\n"

        if not data:
            message = "Нет недоступных продуктов."

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
