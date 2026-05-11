import django_filters

from apps.profile.models import AuditLog, MediaFile, Notification


class MediaFileFilter(django_filters.FilterSet):
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = MediaFile
        fields = ['status', 'bucket', 'mime_type', 'created_from', 'created_to']


class NotificationFilter(django_filters.FilterSet):
    unread = django_filters.BooleanFilter(method='filter_unread')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Notification
        fields = ['type', 'entity_type', 'unread', 'created_from', 'created_to']

    def filter_unread(self, queryset, name, value):
        if value is True:
            return queryset.filter(read_at__isnull=True)
        if value is False:
            return queryset.filter(read_at__isnull=False)
        return queryset


class AuditLogFilter(django_filters.FilterSet):
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = AuditLog
        fields = ['action', 'entity_type', 'actor_user', 'created_from', 'created_to']
