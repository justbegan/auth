from django.contrib import admin

from apps.board.models import (
    BoardFavorite,
    BoardListing,
    BoardListingAttribute,
    BoardListingMedia,
    BoardListingStatsDaily,
    BoardReport,
)


class BoardListingMediaInline(admin.TabularInline):
    model = BoardListingMedia
    extra = 0
    fields = ('media', 'sort_order')
    autocomplete_fields = ('media',)


class BoardListingAttributeInline(admin.TabularInline):
    model = BoardListingAttribute
    extra = 0
    fields = ('key', 'value_text', 'value_num')


@admin.register(BoardListing)
class BoardListingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'seller', 'city', 'category', 'subcategory',
        'status', 'price', 'views_count', 'contacts_count', 'favorites_count',
        'boosted_until', 'created_at',
    )
    list_filter = ('status', 'city', 'category', 'subcategory', 'condition', 'seller_type', 'created_at')
    search_fields = ('title', 'description', 'seller__email', 'seller__phone', 'district', 'address')
    readonly_fields = ('id', 'views_count', 'contacts_count', 'favorites_count', 'created_at', 'updated_at')
    autocomplete_fields = ('city', 'seller', 'category', 'subcategory')
    inlines = (BoardListingMediaInline, BoardListingAttributeInline)
    date_hierarchy = 'created_at'
    list_editable = ('status',)


@admin.register(BoardListingMedia)
class BoardListingMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'media', 'sort_order')
    list_filter = ('listing__city',)
    search_fields = ('listing__title', 'media__object_key')
    readonly_fields = ('id',)
    autocomplete_fields = ('listing', 'media')


@admin.register(BoardListingAttribute)
class BoardListingAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'key', 'value_text', 'value_num')
    list_filter = ('key',)
    search_fields = ('listing__title', 'key', 'value_text')
    readonly_fields = ('id',)
    autocomplete_fields = ('listing',)


@admin.register(BoardFavorite)
class BoardFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'created_at')
    list_filter = ('created_at', 'listing__city')
    search_fields = ('user__email', 'user__phone', 'listing__title')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('user', 'listing')
    date_hierarchy = 'created_at'


@admin.register(BoardListingStatsDaily)
class BoardListingStatsDailyAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'day', 'views', 'contacts', 'favorites')
    list_filter = ('day',)
    search_fields = ('listing__title',)
    autocomplete_fields = ('listing',)
    date_hierarchy = 'day'


@admin.register(BoardReport)
class BoardReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('listing__title', 'reporter__email', 'comment')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('listing', 'reporter')
    list_editable = ('status',)
