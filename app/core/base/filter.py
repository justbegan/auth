import django_filters
from django.db.models import Q


class Base_filter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_method')
    ordering = django_filters.CharFilter(method="ordering_method")

    class Meta:
        abstract = True

    def ordering_method(self, queryset, name, value):
        try:
            if "title" in value:
                value = value.replace("_title", "__title")
            elif "username" in value:
                value = value.replace("_username", "__username")
        except Exception:
            return queryset

    def search_method(self, queryset, name, value):
        return queryset.filter(
            Q(id__icontains=value)
        )
