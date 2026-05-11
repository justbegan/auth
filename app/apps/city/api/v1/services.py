from django.utils import timezone

from core.base.crud import CoreCrud
from apps.city.api.v1.serializers import ChatMessageSerializer, FeedPostSerializer, ReviewSerializer
from apps.city.models import ChatConversation, ChatMessage, FeedPost, Review


class FeedPostServices(CoreCrud):
    model = FeedPost
    serializer = FeedPostSerializer


class ReviewServices(CoreCrud):
    model = Review
    serializer = ReviewSerializer


class ChatMessageServices:
    @staticmethod
    def create_for_conversation(*, conversation: ChatConversation, sender_id, payload: dict):
        serializer = ChatMessageSerializer(
            data={
                **payload,
                'conversation': conversation.id,
                'sender': sender_id,
            }
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=['last_message_at'])
        return ChatMessageSerializer(message).data

    @staticmethod
    def mark_conversation_read(*, conversation: ChatConversation, reader_id):
        read_time = timezone.now()
        updated = ChatMessage.objects.filter(
            conversation=conversation,
            read_at__isnull=True,
        ).exclude(sender_id=reader_id).update(read_at=read_time)
        return {
            'conversation': str(conversation.id),
            'updated': updated,
            'read_at': read_time,
        }
