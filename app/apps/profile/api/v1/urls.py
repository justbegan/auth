from django.urls import path
from . import views


urlpatterns = [
    path('main', views.HelloWorldMain.as_view(), name='main'),
    path('details/<int:pk>', views.HelloWorldDetails.as_view(), name='details'),
]
