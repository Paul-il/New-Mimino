# bot/management/commands/start_bot.py
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import Application
from bot.telegram_bot.handlers import setup_handlers

class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **kwargs):
        # Явное создание цикла событий asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
        setup_handlers(application)
        application.run_polling()
