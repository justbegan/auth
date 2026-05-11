import django_filters
from django.db.models import Q

from apps.admin_panel.models import AdCampaign, AdminStatsDaily, Category, ReviewReport, Tariff
from apps.business.models import Business
from apps.city.models import Review
from apps.user.models import CustomUser


class AdminStatsDailyFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='day', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='day', lookup_expr='lte')

    class Meta:
        model = AdminStatsDaily
        fields = ['city', 'date_from', 'date_to']


class AdminBusinessFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Business
        fields = ['status', 'category', 'city', 'owner', 'created_from', 'created_to', 'q']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))


class AdminReviewFilter(django_filters.FilterSet):
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    q = django_filters.CharFilter(field_name='text', lookup_expr='icontains')

    class Meta:
        model = Review
        fields = ['status', 'business', 'rating_min', 'rating_max', 'q']


class CategoryFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['section', 'parent', 'is_active', 'q']


class AdminUserFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')
    registered_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    registered_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    city_id = django_filters.UUIDFilter(field_name='userprofile__city_id')

    class Meta:
        model = CustomUser
        fields = ['account_type', 'status', 'city_id', 'registered_from', 'registered_to', 'q']

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(phone__icontains=value)
        )


class AdCampaignFilter(django_filters.FilterSet):
    starts_from = django_filters.DateTimeFilter(field_name='starts_at', lookup_expr='gte')
    ends_to = django_filters.DateTimeFilter(field_name='ends_at', lookup_expr='lte')

    class Meta:
        model = AdCampaign
        fields = ['status', 'placement', 'business', 'city', 'starts_from', 'ends_to']


class TariffFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')

    class Meta:
        model = Tariff
        fields = ['target', 'is_active', 'q']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(code__icontains=value) | Q(name__icontains=value))


class ReviewReportFilter(django_filters.FilterSet):
    class Meta:
        model = ReviewReport
        fields = ['status', 'reason', 'review', 'reporter']
