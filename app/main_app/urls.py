from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

START_SYMBOL = ''

urlpatterns = [
    path(f'{START_SYMBOL}admin/', admin.site.urls),
    # Пользовательские роуты
    path(f'{START_SYMBOL}profile/v1/', include('apps.profile.api.v1.urls')),
    path(f'{START_SYMBOL}auth/v1/', include('apps.auth.api.v1.urls')),
    path(f'{START_SYMBOL}user/v1/', include('apps.user.api.v1.urls')),
    path("openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path(f'{START_SYMBOL}docs/', SpectacularSwaggerView.as_view(url_name='schema')),
        path(f'{START_SYMBOL}redoc/', SpectacularRedocView.as_view(url_name='schema')),
    ]
