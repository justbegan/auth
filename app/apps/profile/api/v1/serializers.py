from rest_framework import serializers

from apps.profile.models import AuditLog, MediaFile, Notification, UserProfile


class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = [
            'id',
            'owner',
            'bucket',
            'object_key',
            'url',
            'mime_type',
            'size_bytes',
            'width',
            'height',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'first_name', 'last_name', 'avatar_media', 'city', 'metadata']
        read_only_fields = ['user']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'type',
            'title',
            'body',
            'entity_type',
            'entity_id',
            'read_at',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'read_at']


class AuditLogSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor_user',
            'action',
            'entity_type',
            'entity_id',
            'before_data',
            'after_data',
            'ip_address',
            'created_at',
        ]
        read_only_fields = ['id', 'actor_user', 'created_at', 'ip_address']
