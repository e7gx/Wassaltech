import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_name = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_name}'

        # الانضمام إلى الغرفة
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # مغادرة الغرفة
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        user = self.scope['user']

        # استرجاع المحادثة من قاعدة البيانات
        chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_name)

        # حفظ الرسالة في قاعدة البيانات
        await database_sync_to_async(Message.objects.create)(
            chat=chat,
            sender=user,
            content=message_content
        )

        # إرسال الرسالة إلى المجموعة
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message_content
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # إرسال الرسالة إلى WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
