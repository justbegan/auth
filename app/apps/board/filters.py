import django_filters
from django.db.models import Q

from apps.admin_panel.models import Category
from apps.board.models import BoardFavorite, BoardListing


class BoardCategoryFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['parent', 'q', 'is_active']


class BoardListingFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    with_photo = django_filters.BooleanFilter(method='filter_with_photo')

    class Meta:
        model = BoardListing
        fields = [
            'q', 'category', 'subcategory', 'price_min', 'price_max',
            'condition', 'seller_type', 'district', 'with_photo', 'negotiable',
        ]

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    def filter_with_photo(self, queryset, name, value):
        return queryset.filter(media__isnull=not value).distinct()


class MyBoardListingFilter(BoardListingFilter):
    boosted = django_filters.BooleanFilter(method='filter_boosted')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta(BoardListingFilter.Meta):
        fields = BoardListingFilter.Meta.fields + ['status', 'boosted', 'date_from', 'date_to']

    def filter_boosted(self, queryset, name, value):
        return queryset.filter(boosted_until__isnull=not value)


class BoardFavoriteFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='listing__price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='listing__price', lookup_expr='lte')

    class Meta:
        model = BoardFavorite
        fields = ['listing__category', 'price_min', 'price_max']
