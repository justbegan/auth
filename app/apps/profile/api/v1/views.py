from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profile.api.v1.serializers import (
    AuditLogSerializer,
    MediaFileSerializer,
    NotificationSerializer,
    UserProfileSerializer,
)
from apps.profile.filters import AuditLogFilter, MediaFileFilter, NotificationFilter
from apps.profile.models import AuditLog, MediaFile, Notification, UserProfile
from core.permissions import IsAdminAccount


@extend_schema(tags=['Profile'])
class ProfileMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        profile = self.get_object()
        serializer.save(user=profile.user)
        AuditLog.objects.create(
            actor_user=self.request.user,
            action='profile.update',
            entity_type='user_profile',
            entity_id=profile.user_id,
            after_data=serializer.data,
            ip_address=self.request.META.get('REMOTE_ADDR'),
        )


@extend_schema(tags=['Profile: Media'])
class MediaFileViewSet(viewsets.ModelViewSet):
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MediaFileFilter

    def get_queryset(self):
        return MediaFile.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        media = serializer.save(owner=self.request.user)
        AuditLog.objects.create(
            actor_user=self.request.user,
            action='media_file.create',
            entity_type='media_file',
            entity_id=media.id,
            after_data=serializer.data,
            ip_address=self.request.META.get('REMOTE_ADDR'),
        )


@extend_schema(tags=['Profile: Notifications'])
class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=['read_at'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(read_at__isnull=True).update(read_at=timezone.now())
        return Response({'updated': updated}, status=status.HTTP_200_OK)


@extend_schema(tags=['Profile: Audit'])
class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuditLogFilter

    def get_queryset(self):
        return AuditLog.objects.all().order_by('-created_at')


@extend_schema(tags=['Profile'])
class ProfileMain(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)
