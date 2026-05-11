import django_filters
from django.db.models import Q

from apps.business.models import BusinessAnalyticsDaily, Order, Product


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['q', 'category', 'is_active', 'in_stock', 'price_min', 'price_max']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value) | Q(sku__icontains=value))

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock_qty__gt=0) if value else queryset.filter(stock_qty__lte=0)


class OrderFilter(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    q = django_filters.CharFilter(method='filter_q')

    class Meta:
        model = Order
        fields = ['status', 'delivery_type', 'payment_status', 'date_from', 'date_to', 'q', 'customer']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(id__icontains=value) | Q(customer__email__icontains=value))


class BusinessAnalyticsDailyFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='day', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='day', lookup_expr='lte')

    class Meta:
        model = BusinessAnalyticsDaily
        fields = ['business', 'date_from', 'date_to']
