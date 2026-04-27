from django.urls import path
from . import views


urlpatterns = [
    path('user_main', views.UserMain.as_view(), name='user_main'),
    path('user_details/<int:pk>', views.UserDetails.as_view(), name='user_details'),
    path('current_user', views.CurrentUser.as_view(), name='current_user'),
    path('plusofon', views.Plusofon.as_view(), name='plusofon'),
]
