from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admin_panel.api.v1.serializers import CategorySerializer
from apps.admin_panel.models import Category, ModerationCase
from apps.board.api.v1.serializers import BoardFavoriteSerializer, BoardListingSerializer, BoardReportSerializer
from apps.board.filters import BoardCategoryFilter, BoardFavoriteFilter, BoardListingFilter, MyBoardListingFilter
from apps.board.models import BoardFavorite, BoardListing, BoardReport
from apps.city.api.v1.serializers import ChatConversationSerializer, ChatMessageSerializer
from apps.city.filters import ChatConversationFilter
from apps.city.models import ChatConversation
from apps.profile.models import City


class BoardCityMixin:
    filter_backends = [DjangoFilterBackend]

    def get_city(self):
        return get_object_or_404(City, slug=self.kwargs['city_slug'], is_active=True)

    def is_schema_generation(self):
        return getattr(self, 'swagger_fake_view', False)


@extend_schema(
    tags=['Board: Home'],
    summary='Главная страница доски объявлений',
    description='Возвращает категории и последние активные объявления выбранного города.',
)
class BoardHomeView(BoardCityMixin, APIView):
    permission_classes = [AllowAny]
    serializer_class = BoardListingSerializer

    def get(self, request, city_slug):
        city = self.get_city()
        categories = Category.objects.filter(section=Category.Section.BOARD, parent__isnull=True, is_active=True)
        listings = BoardListing.objects.filter(city=city, status=BoardListing.Status.ACTIVE).order_by('-created_at')[:20]
        return Response({
            'categories': CategorySerializer(categories, many=True).data,
            'popular_queries': [],
            'listings': BoardListingSerializer(listings, many=True).data,
        })


@extend_schema(
    tags=['Board: Categories'],
    summary='Список категорий доски',
    description='Возвращает дерево категорий раздела доски объявлений.',
)
class BoardCategoryListView(BoardCityMixin, generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filterset_class = BoardCategoryFilter

    def get_queryset(self):
        return Category.objects.filter(section=Category.Section.BOARD).order_by('sort_order', 'name')


@extend_schema(
    tags=['Board: Catalog'],
    summary='Каталог объявлений',
    description='Список объявлений по городу с поддержкой фильтров и категории.',
)
class BoardCatalogView(BoardCityMixin, generics.ListAPIView):
    serializer_class = BoardListingSerializer
    permission_classes = [AllowAny]
    filterset_class = BoardListingFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return BoardListing.objects.none()
        queryset = BoardListing.objects.filter(city=self.get_city(), status=BoardListing.Status.ACTIVE)
        category_slug = self.kwargs.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset.order_by('-boosted_until', '-created_at')


@extend_schema(
    tags=['Board: Listing'],
    summary='Карточка объявления',
    description='Возвращает детальную информацию по объявлению.',
)
class BoardItemView(BoardCityMixin, generics.RetrieveAPIView):
    serializer_class = BoardListingSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'listing_id'

    def get_queryset(self):
        if self.is_schema_generation():
            return BoardListing.objects.none()
        return BoardListing.objects.filter(city=self.get_city()).exclude(status=BoardListing.Status.DELETED)


@extend_schema(
    tags=['Board: Listing'],
    summary='Переключить избранное объявления',
    description='Добавляет или удаляет объявление из избранного текущего пользователя.',
)
class BoardItemFavoriteView(BoardCityMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardFavoriteSerializer

    def post(self, request, city_slug, listing_id):
        listing = get_object_or_404(BoardListing, id=listing_id, city=self.get_city())
        favorite, created = BoardFavorite.objects.get_or_create(user=request.user, listing=listing)
        if not created:
            favorite.delete()
        listing.favorites_count = max(0, listing.favorites.count())
        listing.save(update_fields=['favorites_count'])
        return Response({'favorite': created})


@extend_schema(
    tags=['Board: Listing'],
    summary='Запрос контактов продавца',
    description='Увеличивает счетчик обращений по объявлению.',
)
class BoardItemContactView(BoardCityMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardListingSerializer

    def post(self, request, city_slug, listing_id):
        listing = get_object_or_404(BoardListing, id=listing_id, city=self.get_city())
        listing.contacts_count += 1
        listing.save(update_fields=['contacts_count'])
        return Response({'listing_id': listing.id, 'contacts_count': listing.contacts_count})


@extend_schema(
    tags=['Board: Listing'],
    summary='Пожаловаться на объявление',
    description='Создает жалобу на выбранное объявление.',
)
class BoardItemReportView(BoardCityMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardReportSerializer

    def post(self, request, city_slug, listing_id):
        listing = get_object_or_404(BoardListing, id=listing_id, city=self.get_city())
        serializer = BoardReportSerializer(data={**request.data, 'listing': listing.id, 'reporter': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Board: My Listings'],
    summary='Мои объявления',
    description='CRUD для объявлений текущего пользователя в выбранном городе.',
)
class MyBoardListingViewSet(BoardCityMixin, viewsets.ModelViewSet):
    serializer_class = BoardListingSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MyBoardListingFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return BoardListing.objects.none()
        return BoardListing.objects.filter(city=self.get_city(), seller=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        listing = serializer.save(city=self.get_city(), seller=self.request.user, status=BoardListing.Status.REVIEW)
        ModerationCase.objects.create(
            entity_type='listing',
            entity_id=listing.id,
            status=ModerationCase.Status.PENDING,
            submitted_by=self.request.user,
        )

    def destroy(self, request, *args, **kwargs):
        listing = self.get_object()
        listing.status = BoardListing.Status.DELETED
        listing.save(update_fields=['status', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def pause(self, request, city_slug=None, pk=None):
        listing = self.get_object()
        listing.status = BoardListing.Status.PAUSED
        listing.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(listing).data)

    @action(detail=True, methods=['post'])
    def activate(self, request, city_slug=None, pk=None):
        listing = self.get_object()
        listing.status = BoardListing.Status.ACTIVE
        listing.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(listing).data)

    @action(detail=True, methods=['post'])
    def sold(self, request, city_slug=None, pk=None):
        listing = self.get_object()
        listing.status = BoardListing.Status.SOLD
        listing.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(listing).data)

    @action(detail=True, methods=['post'])
    def boost(self, request, city_slug=None, pk=None):
        listing = self.get_object()
        listing.boost()
        return Response(self.get_serializer(listing).data)


@extend_schema(
    tags=['Board: Favorites'],
    summary='Избранные объявления',
    description='Просмотр и удаление избранных объявлений пользователя.',
)
class BoardFavoriteViewSet(BoardCityMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = BoardFavoriteSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = BoardFavoriteFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return BoardFavorite.objects.none()
        return BoardFavorite.objects.filter(user=self.request.user, listing__city=self.get_city()).order_by('-created_at')

    @action(detail=False, methods=['delete'])
    def clear(self, request, city_slug=None):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Board: Favorites'],
    summary='Добавить/удалить объявление из избранного',
    description='Явные endpoint’ы для добавления и удаления избранного по listing_id.',
)
class BoardFavoriteAddView(BoardCityMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardFavoriteSerializer

    def post(self, request, city_slug, listing_id):
        listing = get_object_or_404(BoardListing, id=listing_id, city=self.get_city())
        favorite, created = BoardFavorite.objects.get_or_create(user=request.user, listing=listing)
        listing.favorites_count = listing.favorites.count()
        listing.save(update_fields=['favorites_count'])
        return Response(BoardFavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, city_slug, listing_id):
        listing = get_object_or_404(BoardListing, id=listing_id, city=self.get_city())
        BoardFavorite.objects.filter(user=request.user, listing=listing).delete()
        listing.favorites_count = listing.favorites.count()
        listing.save(update_fields=['favorites_count'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Board: Chats'],
    summary='Чаты по объявлениям',
    description='Список чатов по доске объявлений и отправка сообщений в чат.',
)
class BoardChatViewSet(BoardCityMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ChatConversationSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ChatConversationFilter

    def get_queryset(self):
        if self.is_schema_generation():
            return ChatConversation.objects.none()
        return ChatConversation.objects.filter(city=self.get_city(), kind=ChatConversation.Kind.BOARD).filter(
            buyer=self.request.user
        ) | ChatConversation.objects.filter(city=self.get_city(), kind=ChatConversation.Kind.BOARD).filter(
            seller=self.request.user
        )

    @action(detail=True, methods=['post'], serializer_class=ChatMessageSerializer)
    def messages(self, request, city_slug=None, pk=None):
        conversation = self.get_object()
        serializer = ChatMessageSerializer(data={**request.data, 'conversation': conversation.id, 'sender': request.user.id})
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=['last_message_at'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Board: Create'],
    summary='Справочники для создания объявления',
    description='Возвращает справочные данные для формы создания объявления.',
)
class BoardNewReferencesView(BoardCityMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get(self, request, city_slug):
        categories = Category.objects.filter(section=Category.Section.BOARD, is_active=True)
        return Response({'categories': CategorySerializer(categories, many=True).data})
