from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.profile.api.v1 import views

router = SimpleRouter()
router.register('media', views.MediaFileViewSet, basename='profile-media')
router.register('notifications', views.NotificationViewSet, basename='profile-notifications')
router.register('audit-logs', views.AuditLogViewSet, basename='profile-audit-logs')

urlpatterns = [
    path('me', views.ProfileMeView.as_view(), name='profile-me'),
    path('main', views.ProfileMain.as_view(), name='profile-main'),
    path('', include(router.urls)),
]
