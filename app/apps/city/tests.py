import asyncio

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.city.models import ChatConversation, ChatMessage
from apps.profile.models import City
from apps.user.models import CustomUser
from main_app.asgi import application


@override_settings(
    CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }
)
class CityChatWebSocketTests(TransactionTestCase):
    def setUp(self):
        self.password = 'StrongPass123!'
        self.city = City.objects.create(
            slug='yakutsk',
            name='Yakutsk',
            timezone='Asia/Yakutsk',
            is_active=True,
        )
        self.buyer = CustomUser.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password=self.password,
        )
        self.seller = CustomUser.objects.create_user(
            username='seller@example.com',
            email='seller@example.com',
            password=self.password,
        )
        self.stranger = CustomUser.objects.create_user(
            username='stranger@example.com',
            email='stranger@example.com',
            password=self.password,
        )
        self.conversation = ChatConversation.objects.create(
            city=self.city,
            kind=ChatConversation.Kind.BUSINESS,
            buyer=self.buyer,
            seller=self.seller,
        )
        self.buyer_token = self._access_token(self.buyer)
        self.seller_token = self._access_token(self.seller)
        self.stranger_token = self._access_token(self.stranger)

    def _access_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_city_chat_ws_connect_and_send_message(self):
        async def _test():
            communicator = WebsocketCommunicator(
                application,
                f'/ws/{self.city.slug}/chat/{self.conversation.id}/?token={self.buyer_token}',
            )
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to({'body': 'hello from ws'})
            response = await communicator.receive_json_from()
            self.assertEqual(response.get('body'), 'hello from ws')
            self.assertEqual(response.get('conversation'), str(self.conversation.id))
            self.assertEqual(response.get('sender'), str(self.buyer.id))

            await communicator.disconnect()

        async_to_sync(_test)()
        self.assertTrue(ChatMessage.objects.filter(conversation=self.conversation, body='hello from ws').exists())

    def test_city_chat_ws_rejects_non_participant(self):
        async def _test():
            communicator = WebsocketCommunicator(
                application,
                f'/ws/{self.city.slug}/chat/{self.conversation.id}/?token={self.stranger_token}',
            )
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        async_to_sync(_test)()

    def test_city_chat_ws_broadcasts_read_receipt(self):
        incoming_unread_1 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            body='incoming unread 1',
        )
        incoming_unread_2 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            body='incoming unread 2',
        )
        own_message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            body='own message',
        )
        already_read = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            body='already read',
        )
        already_read.read_at = already_read.created_at
        already_read.save(update_fields=['read_at'])

        async def _test():
            buyer_communicator = WebsocketCommunicator(
                application,
                f'/ws/{self.city.slug}/chat/{self.conversation.id}/?token={self.buyer_token}',
            )
            seller_communicator = WebsocketCommunicator(
                application,
                f'/ws/{self.city.slug}/chat/{self.conversation.id}/?token={self.seller_token}',
            )
            buyer_connected, _ = await buyer_communicator.connect()
            seller_connected, _ = await seller_communicator.connect()
            self.assertTrue(buyer_connected)
            self.assertTrue(seller_connected)

            await seller_communicator.send_json_to({'type': 'chat.read'})

            buyer_event = await asyncio.wait_for(buyer_communicator.receive_json_from(), timeout=3)
            self.assertEqual(buyer_event.get('type'), 'chat.read')
            self.assertEqual(buyer_event.get('conversation'), str(self.conversation.id))
            self.assertEqual(buyer_event.get('reader'), str(self.seller.id))
            self.assertEqual(buyer_event.get('updated'), 2)

            await buyer_communicator.disconnect()
            await seller_communicator.disconnect()

        async_to_sync(_test)()

        incoming_unread_1.refresh_from_db()
        incoming_unread_2.refresh_from_db()
        own_message.refresh_from_db()
        already_read.refresh_from_db()

        self.assertIsNotNone(incoming_unread_1.read_at)
        self.assertIsNotNone(incoming_unread_2.read_at)
        self.assertIsNone(own_message.read_at)
        self.assertIsNotNone(already_read.read_at)


class CityChatReadTests(APITestCase):
    def setUp(self):
        self.password = 'StrongPass123!'
        self.city = City.objects.create(
            slug='yakutsk',
            name='Yakutsk',
            timezone='Asia/Yakutsk',
            is_active=True,
        )
        self.buyer = CustomUser.objects.create_user(
            username='buyer-read@example.com',
            email='buyer-read@example.com',
            password=self.password,
        )
        self.seller = CustomUser.objects.create_user(
            username='seller-read@example.com',
            email='seller-read@example.com',
            password=self.password,
        )
        self.conversation = ChatConversation.objects.create(
            city=self.city,
            kind=ChatConversation.Kind.BUSINESS,
            buyer=self.buyer,
            seller=self.seller,
        )

    def test_mark_read_updates_only_incoming_unread_messages(self):
        own_message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            body='my own message',
        )
        already_read = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            body='already read',
        )
        unread_1 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            body='incoming unread 1',
        )
        unread_2 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            body='incoming unread 2',
        )

        already_read.read_at = already_read.created_at
        already_read.save(update_fields=['read_at'])

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(
            reverse(
                'city-chat-mark-read',
                kwargs={'city_slug': self.city.slug, 'pk': self.conversation.id},
            ),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('updated'), 2)

        own_message.refresh_from_db()
        already_read.refresh_from_db()
        unread_1.refresh_from_db()
        unread_2.refresh_from_db()

        self.assertIsNone(own_message.read_at)
        self.assertIsNotNone(already_read.read_at)
        self.assertIsNotNone(unread_1.read_at)
        self.assertIsNotNone(unread_2.read_at)
