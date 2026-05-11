import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.city.api.v1.services import ChatMessageServices
from apps.city.models import ChatConversation
from apps.profile.models import City


class CityChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.city_slug = self.scope['url_route']['kwargs']['city_slug']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.user = self.scope.get('user')

        self.conversation = await self._get_conversation_if_allowed()
        if not self.conversation:
            await self.close(code=4403)
            return

        self.group_name = f'city_chat_{self.conversation_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            await self.send(text_data=json.dumps({'detail': 'Text payload is required'}))
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'detail': 'Invalid JSON payload'}))
            return

        event_type = payload.get('type', 'chat.message')
        if event_type == 'chat.read':
            read_data, error = await self._mark_read()
            if error:
                await self.send(text_data=json.dumps(error, default=str))
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.read',
                    'message': self._to_json_safe(
                        {
                            'type': 'chat.read',
                            **read_data,
                            'reader': str(self.user.id),
                        }
                    ),
                },
            )
            return

        body = payload.get('body')
        media = payload.get('media')
        if not body and not media:
            await self.send(text_data=json.dumps({'detail': 'Either body or media is required'}))
            return

        message_data, error = await self._create_message(body=body, media_id=media)
        if error:
            await self.send(text_data=json.dumps(error, default=str))
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                # channels_redis uses msgpack and cannot serialize UUID/datetime objects.
                'message': self._to_json_safe(message_data),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message'], default=str))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps(event['message'], default=str))

    @staticmethod
    def _to_json_safe(payload):
        return json.loads(json.dumps(payload, default=str))

    @database_sync_to_async
    def _get_conversation_if_allowed(self):
        user = self.user
        if not user or not user.is_authenticated:
            return None

        city = City.objects.filter(slug=self.city_slug, is_active=True).first()
        if not city:
            return None

        conversation = ChatConversation.objects.filter(id=self.conversation_id, city=city).first()
        if not conversation:
            return None

        if user.id not in {conversation.buyer_id, conversation.seller_id}:
            return None
        return conversation

    @database_sync_to_async
    def _create_message(self, body, media_id):
        try:
            message_data = ChatMessageServices.create_for_conversation(
                conversation=self.conversation,
                sender_id=self.user.id,
                payload={
                    'body': body,
                    'media': media_id,
                },
            )
            return message_data, None
        except Exception as exc:
            detail = getattr(exc, 'detail', str(exc))
            return None, {'detail': detail}

    @database_sync_to_async
    def _mark_read(self):
        try:
            payload = ChatMessageServices.mark_conversation_read(
                conversation=self.conversation,
                reader_id=self.user.id,
            )
            return payload, None
        except Exception as exc:
            detail = getattr(exc, 'detail', str(exc))
            return None, {'detail': detail}
