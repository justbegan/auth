from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('get_token', views.Get_token.as_view(), name='get_token'),
    path('refresh_token', TokenRefreshView.as_view(), name='token_refresh')
]
