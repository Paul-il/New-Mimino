from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)  # Добавляет дату и время отправки сообщения

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} sent at {self.sent_at}"
