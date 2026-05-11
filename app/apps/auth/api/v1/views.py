from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import Request
from drf_spectacular.utils import extend_schema

from .serializers import TokenResponseSerializer, CustomTokenSerializer


@extend_schema(
    methods=["POST"],
    summary="Получить JWT токены",
    description="Авторизация пользователя и выдача access/refresh токенов.",
    responses={200: TokenResponseSerializer},
    tags=['Auth'],
)
class GetToken(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

    def post(self, request: Request, *args, **kwargs):
        """
        Получить jwt токены.
        """
        response = super().post(request, *args, **kwargs)

        if 'refresh' in response.data:
            response.set_cookie(
                key='refresh_token',
                value=response.data['refresh'],
                httponly=False,
                max_age=30 * 24 * 60 * 60,
                secure=False
            )
        if 'access' in response.data:
            response.set_cookie(
                key='access_token',
                value=response.data['access'],
                httponly=False,
                max_age=30 * 24 * 60 * 60,
                secure=False
            )
        return response


@extend_schema(
    methods=["POST"],
    summary="Обновить JWT access токен",
    description="Обновляет access токен по refresh токену.",
    tags=['Auth'],
)
class RefreshToken(TokenRefreshView):
    pass
