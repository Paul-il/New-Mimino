from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Chat, Message
import json


# restaurant_app/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import Chat, Message
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Connected to chat {self.chat_id}")
        print(f"Connected to chat {self.chat_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )
        logger.info(f"Disconnected from chat {self.chat_id}")
        print(f"Disconnected from chat {self.chat_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']

        sender = User.objects.get(username=sender_username)
        chat = Chat.objects.get(id=self.chat_id)

        # Save message to database
        new_message = Message.objects.create(
            chat=chat,
            sender=sender,
            body=message
        )

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        logger.info(f"Message received in chat {self.chat_id}: {message}")
        print(f"Message received in chat {self.chat_id}: {message}")

        # Notify user about new message
        for participant in chat.participants.all():
            await self.channel_layer.group_send(
                f'user_{participant.username}',
                {
                    'type': 'new_message_notification',
                    'message': message,
                    'sender': sender.username,
                    'chat_id': chat.id
                }
            )
            logger.info(f"Notification sent to user {participant.username} for chat {self.chat_id}")
            print(f"Notification sent to user {participant.username} for chat {self.chat_id}")

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))
        logger.info(f"Message sent to WebSocket for chat {self.chat_id}: {message}")
        print(f"Message sent to WebSocket for chat {self.chat_id}: {message}")

    async def new_message_notification(self, event):
        # Send new message notification to WebSocket
        await self.send(text_data=json.dumps({
            'notification': 'new_message',
            'message': event['message'],
            'sender': event['sender'],
            'chat_id': event['chat_id']
        }))
        logger.info(f"Notification sent to WebSocket: {event['message']}")
        print(f"Notification sent to WebSocket: {event['message']}")


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_add(
                f'user_{user.username}',
                self.channel_name
            )
            await self.accept()
            logger.info(f'User {user.username} connected to notifications')
            print(f'User {user.username} connected to notifications')
        else:
            await self.close()
            logger.info(f'User {user.username} is not authenticated')
            print(f'User {user.username} is not authenticated')

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_discard(
                f'user_{user.username}',
                self.channel_name
            )
            logger.info(f'User {user.username} disconnected from notifications')
            print(f'User {user.username} disconnected from notifications')

    async def new_message_notification(self, event):
        await self.send(text_data=json.dumps({
            'notification': 'new_message',
            'message': event['message'],
            'sender': event['sender'],
            'chat_id': event['chat_id']
        }))
        logger.info(f'Sending notification to user: {self.scope["user"].username}')
        print(f'Sending notification to user: {self.scope["user"].username}')