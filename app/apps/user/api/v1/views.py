from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import Response, APIView, Request
from drf_spectacular.utils import extend_schema

from apps.user.api.v1.services import User_services
from apps.user.api.v1.serializers import (User_serializer, Plusofon_serializer)
from apps.user.models import CustomUser
from apps.user.filters import Custom_user_filter


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


class User_main(generics.ListCreateAPIView):
    """
    Получить всех пользователей
    """
    serializer_class = User_serializer
    queryset = CustomUser.objects.all().order_by('-id')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = Custom_user_filter

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
        data['is_active'] = False
        return Response(User_services.create(data))


class Plusofon(APIView):
    serializer_class = Plusofon_serializer

    def post(self, request: Request):
        data = request.data
        number_list = data.get('from', [])
        if len(number_list) == 0:
            return Response({"ok": False})

        number = number_list[0]
        verify = User_services.plusofon_verify(number)
        if not verify:
            return Response({"ok": False})
        return Response({"ok": True})
