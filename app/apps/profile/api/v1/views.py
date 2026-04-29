from rest_framework.views import (APIView, Request, Response)
from drf_spectacular.utils import extend_schema


@extend_schema(
    methods=["GET"],
    summary="Приветствие",
)
class HelloWorldMain(APIView):
    def get(self, request: Request) -> Response:
        return Response({'hello': 'world'})


@extend_schema(
    methods=["GET"],
    summary="Приветствие с параметром",
)
class HelloWorldDetails(APIView):
    def get(self, request: Request, pk: int) -> Response:
        return Response({'hello': f'world {pk}'})
