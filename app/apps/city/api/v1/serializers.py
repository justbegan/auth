from rest_framework import serializers

from apps.business.api.v1.serializers import BusinessSerializer, OrderSerializer, ProductSerializer
from apps.city.models import (
    AIRequest,
    ChatConversation,
    ChatMessage,
    FeedComment,
    FeedPost,
    FeedPostMedia,
    FeedReaction,
    Follow,
    Review,
    Story,
    StorySlide,
)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class FeedPostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedPostMedia
        fields = '__all__'


class FeedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedComment
        fields = '__all__'


class FeedReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedReaction
        fields = '__all__'


class FeedPostSerializer(serializers.ModelSerializer):
    media = FeedPostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = FeedPost
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class StorySlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorySlide
        fields = '__all__'


class StorySerializer(serializers.ModelSerializer):
    slides = StorySlideSerializer(many=True, read_only=True)

    class Meta:
        model = Story
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatConversationSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatConversation
        fields = '__all__'


class AIRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRequest
        fields = '__all__'
        read_only_fields = ['response']


class CityBusinessDetailSerializer(BusinessSerializer):
    products = ProductSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)


class CityOrderSerializer(OrderSerializer):
    pass
