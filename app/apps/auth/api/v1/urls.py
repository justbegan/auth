from django.urls import path
from . import views


urlpatterns = [
    path('get_token', views.GetToken.as_view(), name='get_token'),
    path('refresh_token', views.RefreshToken.as_view(), name='token_refresh')
]
