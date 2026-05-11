from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken, TokenError

from apps.user.models import CustomUser


@database_sync_to_async
def _get_user_from_token(token: str):
    try:
        payload = AccessToken(token)
    except TokenError:
        return AnonymousUser()
    user_id = payload.get('user_id')
    if not user_id:
        return AnonymousUser()
    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return AnonymousUser()


class JwtQueryAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get('user') and scope['user'].is_authenticated:
            return await self.inner(scope, receive, send)

        query_string = scope.get('query_string', b'').decode('utf-8')
        token = parse_qs(query_string).get('token', [None])[0]
        if token:
            scope['user'] = await _get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        return await self.inner(scope, receive, send)


def JwtQueryAuthMiddlewareStack(inner):
    return JwtQueryAuthMiddleware(inner)
