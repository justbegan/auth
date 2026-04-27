from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import Request
from drf_spectacular.utils import extend_schema

from .serializers import TokenResponseSerializer, CustomTokenSerializer


@extend_schema(
    methods=["POST"],
    summary="Получить jwt токен",
    responses={200: TokenResponseSerializer}
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
