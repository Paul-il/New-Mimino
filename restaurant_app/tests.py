from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

import django
from django.conf import settings

settings.configure(DEFAULT_SETTINGS_MODULE='restaurant_project.settings')
django.setup()

# Теперь вы можете импортировать модели и прочие компоненты Django


class SendPrintNotificationTest(TestCase):
    def setUp(self):
        # Создание тестового пользователя и вход в систему
        self.client = Client()
        self.test_user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Создайте здесь объекты, необходимые для тестирования

    def test_send_notification(self):
        url = reverse('send_print_notification', args=[1])  # Предполагается, что заказ с ID=1 существует
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        # Дополнительные проверки ответа
