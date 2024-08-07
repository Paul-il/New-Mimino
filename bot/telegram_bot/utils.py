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

async def get_delivery_data(update: Update, context: CallbackContext) -> None:
    selected_date_str = update.message.text if update.message.text else datetime.now().strftime('%Y-%m-%d')
    url = 'http://127.0.0.1:31337/api/delivery_summary/'  # URL для получения данных о доставках

    try:
        response = requests.get(url, params={'date': selected_date_str})
        response.raise_for_status()
        
        # Печать содержимого ответа для отладки
        logger.info(f"Ответ от сервера: {response.text}")

        # Попытка парсинга JSON
        data = response.json()

        # Обработка данных и создание сообщения для Telegram
        message = f"Сводка по доставке на {selected_date_str}:\n\n"
        for order in data['delivery_orders']:
            message += (
                f"Курьер: {order['courier']}\n"
                f"Город доставки: {order['city']}\n"
                f"Адрес доставки: {order['address']}\n"
                f"Номер телефона: {order['phone']}\n"
                f"Сумма заказа: {order['total_amount']}\n"
                f"Метод оплаты: {order['payment_method']}\n"
                f"Время заказа: {order['delivery_time']}\n\n"
            )
        message += (
            f"Общая сумма всех заказов: {data['all_orders_total']}₪\n"
            f"Сумма заказов, оплаченных наличными Соло: {data['solo_cash_orders_total']}₪\n"
            f"Сумма заказов, оплаченных наличными Стасу: {data['our_courier_cash_orders_total']}₪\n"
            f"Сумма, которую должен вернуть Стас: {data['our_courier_cash_orders_after_discount']}₪\n"
        )

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))

async def get_bookings(update: Update, context: CallbackContext) -> None:
    selected_date_str = update.message.text if update.message.text else datetime.now().strftime('%Y-%m-%d')
    url = 'http://127.0.0.1:31337/api/booking_summary/'  # URL для получения данных о бронях

    try:
        response = requests.get(url, params={'date': selected_date_str})
        response.raise_for_status()
        
        # Печать содержимого ответа для отладки
        logger.info(f"Ответ от сервера: {response.text}")

        # Попытка парсинга JSON
        data = response.json()

        # Обработка данных и создание сообщения для Telegram
        message = f"Бронирования на {selected_date_str}:\n\n"
        for booking in data:
            message += (
                f"Кто делал бронь: {booking['user']}\n"
                f"Номер стола: {booking['table']}\n"
                f"Дата бронирования: {booking['reserved_date']}\n"
                f"Время бронирования: {booking['reserved_time']}\n"
                f"Количество людей: {booking['num_of_people']}\n"
                f"Описание: {booking['description']}\n\n"
            )

        message += "Хотите выбрать другую дату? Напишите /choose_date."

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке"), KeyboardButton("Забронированные столы")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))

async def choose_date(update: Update, context: CallbackContext) -> None:
    url = 'http://127.0.0.1:31337/api/available_booking_dates/'  # URL для получения доступных дат

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Печать содержимого ответа для отладки
        logger.info(f"Ответ от сервера: {response.text}")

        # Попытка парсинга JSON
        data = response.json()

        # Создание кнопок с доступными датами
        buttons = [[KeyboardButton(date)] for date in data['available_dates']]
        buttons.append([KeyboardButton("Меню")])
        
        await update.message.reply_text(
            'Выберите одну из доступных дат:',
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.')
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.')