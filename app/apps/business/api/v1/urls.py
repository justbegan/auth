from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.business.api.v1 import views

router = SimpleRouter()
router.register('products', views.ProductViewSet, basename='dashboard-products')
router.register('orders', views.DashboardOrderViewSet, basename='dashboard-orders')
router.register('analytics', views.DashboardAnalyticsViewSet, basename='dashboard-analytics')

urlpatterns = [
    path('overview', views.DashboardOverview.as_view(), name='dashboard-overview'),
    path('profile', views.DashboardProfile.as_view(), name='dashboard-profile'),
    path('', include(router.urls)),
]
