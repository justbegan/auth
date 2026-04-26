from django.urls import path
from . import views


urlpatterns = [
    path('user_main', views.User_main.as_view(), name='user_main'),
    path('plusofon', views.Plusofon.as_view(), name='plusofon'),
]
