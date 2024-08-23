import json
import logging
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json['message']
            user = self.scope['user']

            if not user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'error': 'User is not authenticated'
                }))
                return

            chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
            await database_sync_to_async(Message.objects.create)(
                chat=chat,
                sender=user,
                content=message_content
            )

            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content
                }
            )

        except Chat.DoesNotExist:
            await self.send(text_data=json.dumps({
                'error': 'Chat not found'
            }))
            logger.error(f'Chat with id {self.chat_id} not found.')
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
            logger.error(f'Invalid JSON received: {text_data}')
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': 'An error occurred'
            }))
            logger.error(f'Unexpected error: {str(e)}')

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
