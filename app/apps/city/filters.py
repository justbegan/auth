import django_filters
from django.db.models import Q

from apps.business.models import Business, Order
from apps.city.models import ChatConversation, FeedPost


class CityBusinessFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    delivery = django_filters.BooleanFilter(method='noop')
    pickup = django_filters.BooleanFilter(method='noop')
    open_now = django_filters.BooleanFilter(method='noop')

    class Meta:
        model = Business
        fields = ['q', 'category', 'rating_min', 'delivery', 'pickup', 'open_now']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

    def noop(self, queryset, name, value):
        return queryset


class CitySearchFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')
    price_min = django_filters.NumberFilter(field_name='products__price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='products__price', lookup_expr='lte')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')

    class Meta:
        model = Business
        fields = ['q', 'category', 'rating_min', 'price_min', 'price_max']

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(products__name__icontains=value)
        ).distinct()


class FeedPostFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(method='filter_tag')
    date_from = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')

    class Meta:
        model = FeedPost
        fields = ['type', 'business', 'tag', 'date_from', 'date_to']

    def filter_tag(self, queryset, name, value):
        return queryset.filter(tags__contains=[value])


class CityOrderFilter(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    q = django_filters.CharFilter(method='filter_q')

    class Meta:
        model = Order
        fields = ['status', 'delivery_type', 'payment_status', 'date_from', 'date_to', 'q']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(business__name__icontains=value) | Q(items__name_snapshot__icontains=value)).distinct()


class ChatConversationFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')

    class Meta:
        model = ChatConversation
        fields = ['kind', 'order', 'business', 'q']

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(messages__body__icontains=value)).distinct()
