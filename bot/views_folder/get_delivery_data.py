import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

async def get_delivery_data(update: Update, context: CallbackContext) -> None:
    url = 'http://127.0.0.1:31337/api/delivery_summary/'  # URL для получения данных по доставке
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Печать содержимого ответа для отладки
        logger.info(f"Ответ от сервера: {response.text}")

        # Попытка парсинга JSON
        data = response.json()

        # Обработка данных и создание сообщения для Telegram
        message = (
            f"Сводка по доставке на {data['selected_date']}:\n\n"
            f"Общая сумма всех заказов: {data['all_orders_total']}₪\n\n"
            f"Заказы, оплаченные наличными Соло: {data['solo_cash_orders_total']}₪\n\n"
            f"Заказы, оплаченные наличными Стасу: {data['our_courier_cash_orders_total']}₪\n"
            f"Сумма, которую должен вернуть Стас: {data['our_courier_cash_orders_after_discount']}₪\n\n"
            f"Детали заказов:\n"
        )

        for order in data['delivery_orders']:
            message += (
                f"Номер заказа: {order['id']}\n"
                f"Курьер: {order['courier__name']}\n"
                f"Город: {order['customer__city']}\n"
                f"Адрес: {order['customer__street']} {order['customer__house_number']}\n"
                f"Телефон: {order['customer__delivery_phone_number']}\n"
                f"Сумма заказа: {order['total_amount']}₪\n"
                f"Метод оплаты: {order['payment_method']}\n"
                f"Время заказа: {order['delivery_date']} {order['delivery_time']}\n\n"
            )

        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        await update.message.reply_text('Произошла ошибка при получении данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
    except ValueError as e:
        logger.error(f"Ошибка при парсинге JSON: {e}")
        await update.message.reply_text('Ошибка при обработке данных с сайта.', reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Сводка"), KeyboardButton("Чаевые официантов")],
            [KeyboardButton("Открытые столы"), KeyboardButton("Недоступные продукты")],
            [KeyboardButton("Сводка по доставке")],
            [KeyboardButton("Другие команды")]
        ], resize_keyboard=True))
