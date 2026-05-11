from django.core.cache import cache
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})


class ReadinessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
        }
        is_ready = all(checks.values())
        http_status = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response({'status': 'ready' if is_ready else 'not_ready', 'checks': checks}, status=http_status)

    @staticmethod
    def _check_database():
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            return True
        except Exception:
            return False

    @staticmethod
    def _check_cache():
        try:
            cache.set('healthcheck_key', 'ok', timeout=5)
            return cache.get('healthcheck_key') == 'ok'
        except Exception:
            return False
