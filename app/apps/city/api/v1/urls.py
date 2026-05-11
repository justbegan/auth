from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.city.api.v1 import views

router = SimpleRouter()
router.register('feed', views.CityFeedViewSet, basename='city-feed')
router.register('orders', views.CityOrderViewSet, basename='city-orders')
router.register('chat', views.CityChatViewSet, basename='city-chat')
router.register('ai', views.CityAIViewSet, basename='city-ai')

urlpatterns = [
    path('map', views.CityMapView.as_view(), name='city-map'),
    path('business/<uuid:business_id>', views.CityBusinessDetailView.as_view(), name='city-business-detail'),
    path(
        'business/<uuid:business_id>/favorite', views.CityBusinessFavoriteView.as_view(), name='city-business-favorite'
    ),
    path('business/<uuid:business_id>/share', views.CityBusinessShareView.as_view(), name='city-business-share'),
    path('search', views.CitySearchView.as_view(), name='city-search'),
    path('auth/register', views.CityAuthRegisterView.as_view(), name='city-auth-register'),
    path('auth/login', views.CityAuthLoginView.as_view(), name='city-auth-login'),
    path('auth/otp/request', views.CityAuthOTPRequestView.as_view(), name='city-auth-otp-request'),
    path('auth/otp/verify', views.CityAuthOTPVerifyView.as_view(), name='city-auth-otp-verify'),
    path('auth/logout', views.CityAuthLogoutView.as_view(), name='city-auth-logout'),
    path('', include(router.urls)),
]
