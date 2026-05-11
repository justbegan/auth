from django.urls import re_path

from apps.city.consumers import CityChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/(?P<city_slug>[-a-zA-Z0-9_]+)/chat/(?P<conversation_id>[0-9a-fA-F-]+)/$', CityChatConsumer.as_asgi()),
]
