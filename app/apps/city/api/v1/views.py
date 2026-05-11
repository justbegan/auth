from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.business.models import Business, Order
from apps.city.api.v1.serializers import (
    AIRequestSerializer,
    ChatConversationSerializer,
    ChatMessageSerializer,
    CityBusinessDetailSerializer,
    CityOrderSerializer,
    FeedCommentSerializer,
    FeedPostSerializer,
    ReviewSerializer,
)
from apps.city.api.v1.services import ChatMessageServices
from apps.city.filters import (
    ChatConversationFilter,
    CityBusinessFilter,
    CityOrderFilter,
    CitySearchFilter,
    FeedPostFilter,
)
from apps.city.models import AIRequest, ChatConversation, FeedPost, FeedReaction
from apps.profile.models import City
from apps.user.api.v1.serializers import UserSerializer
from core.permissions import IsAuthenticatedOrReadOnlyForCity


class CityMixin:
    filter_backends = [DjangoFilterBackend]

    def get_city(self):
        return get_object_or_404(City, slug=self.kwargs['city_slug'], is_active=True)

    def is_schema_generation(self):
        return getattr(self, 'swagger_fake_view', False)


@extend_schema(
    tags=['City: Map'],
    summary='Карта города и список бизнесов',
    description='Возвращает список активных бизнесов города для отображения на карте.',
)
class CityMapView(CityMixin, generics.ListAPIView):
    serializer_class = CityBusinessDetailSerializer
    filterset_class = CityBusinessFilter
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.is_schema_generation():
            return Business.objects.none()
        return Business.objects.filter(city=self.get_city(), status=Business.Status.ACTIVE).order_by('-rating', 'name')


@extend_schema(
    tags=['City: Businesses'],
    summary='Детальная информация о бизнесе',
    description='Возвращает карточку активного бизнеса выбранного города.',
)
class CityBusinessDetailView(CityMixin, generics.RetrieveAPIView):
    serializer_class = CityBusinessDetailSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'business_id'

    def get_queryset(self):
        if self.is_schema_generation():
            return Business.objects.none()
        return Business.objects.filter(city=self.get_city(), status=Business.Status.ACTIVE)


@extend_schema(
    tags=['City: Businesses'],
    summary='Добавить бизнес в избранное',
    description='Помечает бизнес как избранный для текущего пользователя.',
)
class CityBusinessFavoriteView(CityMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CityBusinessDetailSerializer

    def post(self, request, city_slug, business_id):
        business = get_object_or_404(Business, id=business_id, city=self.get_city())
        return Response({'business_id': business.id, 'favorite': True})


@extend_schema(
    tags=['City: Businesses'],
    summary='Поделиться бизнесом',
    description='Фиксирует действие "поделиться" для карточки бизнеса.',
)
class CityBusinessShareView(CityMixin, APIView):
    permission_classes = [AllowAny]
    serializer_class = CityBusinessDetailSerializer

    def post(self, request, city_slug, business_id):
        business = get_object_or_404(Business, id=business_id, city=self.get_city())
        return Response({'business_id': business.id, 'shared': True})


@extend_schema(
    tags=['City: Search'],
    summary='Поиск по бизнесам города',
    description='Ищет активные бизнесы по параметрам фильтра в выбранном городе.',
)
class CitySearchView(CityMixin, generics.ListAPIView):
    serializer_class = CityBusinessDetailSerializer
    filterset_class = CitySearchFilter
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.is_schema_generation():
            return Business.objects.none()
        return Business.objects.filter(city=self.get_city(), status=Business.Status.ACTIVE).distinct()


@extend_schema(
    tags=['City: Feed'],
    summary='Лента города',
    description='CRUD для публикаций городской ленты и связанных действий.',
)
class CityFeedViewSet(CityMixin, viewsets.ModelViewSet):
    serializer_class = FeedPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyForCity]
    filterset_class = FeedPostFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return FeedPost.objects.none()
        return FeedPost.objects.filter(city=self.get_city()).order_by('-published_at', '-created_at')

    def perform_create(self, serializer):
        serializer.save(city=self.get_city(), author_user=self.request.user, published_at=timezone.now())

    @action(detail=True, methods=['post'])
    def like(self, request, city_slug=None, pk=None):
        post = self.get_object()
        reaction, created = FeedReaction.objects.get_or_create(post=post, user=request.user, reaction='like')
        if not created:
            reaction.delete()
        return Response({'liked': created})

    @action(detail=True, methods=['post'], serializer_class=FeedCommentSerializer)
    def comments(self, request, city_slug=None, pk=None):
        post = self.get_object()
        serializer = FeedCommentSerializer(data={**request.data, 'post': post.id, 'user': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def hide(self, request, city_slug=None, pk=None):
        post = self.get_object()
        can_hide = (
            post.author_user_id == request.user.id
            or request.user.is_staff
            or getattr(request.user, 'account_type', None) == 'admin'
        )
        if not can_hide:
            return Response({'detail': 'You do not have permission to hide this post.'}, status=status.HTTP_403_FORBIDDEN)
        post.status = FeedPost.Status.HIDDEN
        post.save(update_fields=['status'])
        return Response(self.get_serializer(post).data)


@extend_schema(
    tags=['City: Orders'],
    summary='Заказы пользователя в городе',
    description='Просмотр списка и деталей заказов текущего пользователя.',
)
class CityOrderViewSet(CityMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CityOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CityOrderFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return Order.objects.none()
        return Order.objects.filter(city=self.get_city(), customer=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def cancel(self, request, city_slug=None, pk=None):
        order = self.get_object()
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=['post'], serializer_class=ReviewSerializer)
    def rate(self, request, city_slug=None, pk=None):
        order = self.get_object()
        serializer = ReviewSerializer(data={
            **request.data,
            'business': order.business_id,
            'user': request.user.id,
            'order': order.id,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    @extend_schema(
        summary='Повторить заказ (не рабочее)',
        description='Заглушка MVP. Черновик повторного заказа пока не создается (не рабочее).',
    )
    def repeat(self, request, city_slug=None, pk=None):
        order = self.get_object()
        return Response({'source_order_id': order.id, 'detail': 'Repeat order draft is not created in MVP'})


@extend_schema(
    tags=['City: Chats'],
    summary='Чаты города',
    description='Просмотр чатов пользователя и отправка сообщений в выбранный чат.',
)
class CityChatViewSet(CityMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ChatConversationFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return ChatConversation.objects.none()
        user = self.request.user
        return ChatConversation.objects.filter(
            city=self.get_city()).filter(buyer=user) | ChatConversation.objects.filter(
            city=self.get_city()
        ).filter(seller=user)

    @action(detail=True, methods=['post'], serializer_class=ChatMessageSerializer)
    def messages(self, request, city_slug=None, pk=None):
        conversation = self.get_object()
        message_data = ChatMessageServices.create_for_conversation(
            conversation=conversation,
            sender_id=request.user.id,
            payload=request.data,
        )
        return Response(message_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, city_slug=None, pk=None):
        conversation = self.get_object()
        payload = ChatMessageServices.mark_conversation_read(
            conversation=conversation,
            reader_id=request.user.id,
        )
        return Response(payload, status=status.HTTP_200_OK)


@extend_schema(
    tags=['City: AI Assistant'],
    summary='AI-запросы города (не рабочее)',
    description='Временная заглушка MVP: реальная AI-интеграция не подключена (не рабочее).',
)
class CityAIViewSet(CityMixin, mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AIRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.is_schema_generation():
            return AIRequest.objects.none()
        return AIRequest.objects.filter(city=self.get_city(), user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(
            city=self.get_city(),
            user=self.request.user,
            response={'items': [], 'message': 'AI integration is not connected in MVP'},
        )


@extend_schema(
    tags=['City: Auth'],
    summary='Регистрация пользователя города',
    description='Создает нового пользователя с ролью user в контексте выбранного города.',
)
class CityAuthRegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, city_slug):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(account_type='user')
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['City: Auth'],
    summary='Логин пользователя города',
    description='Возвращает JWT-пару токенов для пользователя выбранного города.',
)
class CityAuthLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer

    def post(self, request, city_slug):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


@extend_schema(
    tags=['City: Auth'],
    summary='Запрос OTP-кода (не рабочее)',
    description='Заглушка MVP. Провайдер OTP не подключен (не рабочее).',
)
class CityAuthOTPRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, city_slug):
        return Response({'ok': True, 'detail': 'OTP provider is not connected in MVP'})


@extend_schema(
    tags=['City: Auth'],
    summary='Подтверждение OTP-кода (не рабочее)',
    description='Заглушка MVP. Проверка OTP не реализована (не рабочее).',
)
class CityAuthOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, city_slug):
        return Response({'ok': True, 'detail': 'OTP provider is not connected in MVP'})


@extend_schema(
    tags=['City: Auth'],
    summary='Выход пользователя',
    description='Завершает сессию пользователя на уровне API (logout).',
)
class CityAuthLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, city_slug):
        return Response(status=status.HTTP_204_NO_CONTENT)
