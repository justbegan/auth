import django_filters
from django.db.models import Q

from .models import CustomUser


class CustomUserFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(method='filter_id')
    q = django_filters.CharFilter(method='filter_q')
    registered_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    registered_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_active = django_filters.NumberFilter(
        method='filter_is_active',
        label="Фильтрация по статусу активности (2 = все, 1 = активен, 0 = неактивен)",
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'is_active', 'account_type', 'status',
            'registered_from', 'registered_to', 'q',
        ]

    def filter_id(self, queryset, name, value):
        return queryset.filter(id=value)

    def filter_q(self, queryset, name, value):
        if value in django_filters.constants.EMPTY_VALUES:
            return queryset
        return queryset.filter(
            Q(email__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(phone__icontains=value)
        )

    def filter_is_active(self, queryset, name, value: str):
        value = int(value)
        if value == 0:
            return queryset.filter(is_active=False)
        elif value == 1:
            return queryset.filter(is_active=True)
        else:
            return queryset
