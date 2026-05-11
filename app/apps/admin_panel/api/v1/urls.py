from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.admin_panel.api.v1 import views

router = SimpleRouter()
router.register('stats', views.AdminStatsViewSet, basename='admin-stats')
router.register('businesses', views.AdminBusinessViewSet, basename='admin-businesses')
router.register('reviews', views.AdminReviewViewSet, basename='admin-reviews')
router.register('reviews/reports', views.ReviewReportViewSet, basename='admin-review-reports')
router.register('categories', views.CategoryViewSet, basename='admin-categories')
router.register('users', views.AdminUserViewSet, basename='admin-users')
router.register('ads', views.AdCampaignViewSet, basename='admin-ads')
router.register('tariffs', views.TariffViewSet, basename='admin-tariffs')

urlpatterns = [
    path('', include(router.urls)),
]
