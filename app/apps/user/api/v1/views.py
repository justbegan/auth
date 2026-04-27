from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import Response, APIView, Request
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


class UserMain(generics.ListCreateAPIView):
    """
    Получить всех пользователей
    """
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all().order_by('-id')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomUserFilter

    def get_queryset(self):
        return super().get_queryset()

    @extend_schema(
        methods=["POST"],
        summary="Регистрация нового пользователя",
    )
    def post(self, request, *args, **kwargs):
        """
        Создание нового пользователя
        """
        data = request.data
        return Response(UserServices.create(data))


class UserDetails(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class CurrentUser(APIView):
    serializer_class = UserSerializer

    def get(self, request: Request):
        return Response(UserServices.get(parameters={
            "id": request.user.id
        }))


class Plusofon(APIView):
    serializer_class = PlusofonSerializer

    def post(self, request: Request):
        number = request.POST.get("from")
        if not number:
            return Response({"ok": False}, status=500)
        verify = UserServices.plusofon_verify(number)
        if not verify:
            return Response({"ok": False}, status=500)
        return Response({"ok": True})
