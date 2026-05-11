from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.health import HealthView, ReadinessView
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

START_SYMBOL = ''

urlpatterns = [
    path(f'{START_SYMBOL}health/', HealthView.as_view(), name='health'),
    path(f'{START_SYMBOL}ready/', ReadinessView.as_view(), name='ready'),
    path(f'{START_SYMBOL}admin/', admin.site.urls),
    path(f'{START_SYMBOL}api/v1/admin-panel/', include('apps.admin_panel.api.v1.urls')),
    path(f'{START_SYMBOL}api/v1/dashboard/', include('apps.business.api.v1.urls')),
    path(f'{START_SYMBOL}api/v1/<slug:city_slug>/city/', include('apps.city.api.v1.urls')),
    path(f'{START_SYMBOL}api/v1/<slug:city_slug>/board/', include('apps.board.api.v1.urls')),
    path(f'{START_SYMBOL}api/v1/profile/', include('apps.profile.api.v1.urls')),
    path(f'{START_SYMBOL}api/v1/auth/', include('apps.auth.api.v1.urls')),
    path(f'{START_SYMBOL}api/v1/user/', include('apps.user.api.v1.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path("openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
        path(f'{START_SYMBOL}docs/', SpectacularSwaggerView.as_view(url_name='schema')),
        path(f'{START_SYMBOL}redoc/', SpectacularRedocView.as_view(url_name='schema')),
    ]
