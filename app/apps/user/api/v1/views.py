import hmac

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import Response, APIView, Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from drf_spectacular.utils import extend_schema

from apps.user.api.v1.services import UserServices
from apps.user.api.v1.serializers import (UserSerializer, PlusofonSerializer)
from apps.user.models import CustomUser
from apps.user.filters import CustomUserFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


@extend_schema(
    tags=['Users'],
    summary='Список и регистрация пользователей',
    description='GET: список пользователей (требуется авторизация). POST: регистрация нового пользователя.',
)
class UserMain(generics.ListCreateAPIView):
    """
    Получить всех пользователей
    """
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all().order_by('-id')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomUserFilter
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        return super().get_queryset()

    @extend_schema(
        methods=["POST"],
        summary="Регистрация нового пользователя",
        description="Создает нового пользователя. Для публичной регистрации доступен без авторизации.",
        tags=['Users'],
    )
    def post(self, request, *args, **kwargs):
        """
        Создание нового пользователя
        """
        data = request.data
        return Response(UserServices.create(data, context={'request': request}))


@extend_schema(
    tags=['Users'],
    summary='Детали пользователя',
    description='Получение и обновление профиля пользователя. Для обычного пользователя доступно только свое.',
)
class UserDetails(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'account_type', None) == 'admin':
            return super().get_queryset()
        return super().get_queryset().filter(id=user.id)


@extend_schema(
    tags=['Users'],
    summary='Текущий пользователь',
    description='Возвращает данные текущего авторизованного пользователя.',
)
class CurrentUser(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return Response(UserServices.get(parameters={
            "id": request.user.id
        }))


@extend_schema(
    tags=['Users: Phone Verification'],
    summary='Webhook подтверждения телефона',
    description='Принимает callback от Plusofon и подтверждает пользователя по номеру телефона.',
)
class Plusofon(APIView):
    serializer_class = PlusofonSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request):
        provided_token = request.headers.get("X-Plusofon-Token", "")
        expected_token = settings.PLUSOFON_WEBHOOK_TOKEN
        if not expected_token or not hmac.compare_digest(provided_token, expected_token):
            return Response({"ok": False}, status=403)
        number = request.POST.get("from")
        if not number:
            return Response({"ok": False}, status=500)
        verify = UserServices.plusofon_verify(number)
        if not verify:
            return Response({"ok": False}, status=500)
        return Response({"ok": True})
