from django.contrib import admin

from apps.business.models import (
    Business,
    BusinessAnalyticsDaily,
    BusinessLocation,
    BusinessWorkingHours,
    Order,
    OrderItem,
    Product,
    ProductImportJob,
)


class BusinessLocationInline(admin.TabularInline):
    model = BusinessLocation
    extra = 0
    fields = ('address', 'district', 'point', 'geohash', 'is_main')


class BusinessWorkingHoursInline(admin.TabularInline):
    model = BusinessWorkingHours
    extra = 0
    fields = ('day_of_week', 'open_time', 'close_time', 'is_closed')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'name_snapshot', 'qty', 'price', 'total')
    readonly_fields = ('total',)


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'owner', 'city', 'category', 'status',
        'rating', 'reviews_count', 'created_at',
    )
    list_filter = ('status', 'city', 'category', 'created_at')
    search_fields = ('name', 'slug', 'description', 'owner__email', 'phone', 'email')
    readonly_fields = ('id', 'rating', 'reviews_count', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('owner', 'city', 'category', 'logo_media', 'cover_media')
    inlines = (BusinessLocationInline, BusinessWorkingHoursInline)
    fieldsets = (
        ('Основное', {'fields': ('id', 'owner', 'city', 'category', 'name', 'slug', 'description', 'status')}),
        ('Контакты', {'fields': ('phone', 'email', 'website')}),
        ('Медиа', {'fields': ('logo_media', 'cover_media')}),
        ('Метрики', {'fields': ('rating', 'reviews_count')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'address', 'district', 'lat', 'lng', 'is_main')
    list_filter = ('is_main', 'district')
    search_fields = ('business__name', 'address', 'district', 'geohash')
    readonly_fields = ('id',)
    autocomplete_fields = ('business',)


@admin.register(BusinessWorkingHours)
class BusinessWorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'day_of_week', 'open_time', 'close_time', 'is_closed')
    list_filter = ('day_of_week', 'is_closed')
    search_fields = ('business__name',)
    readonly_fields = ('id',)
    autocomplete_fields = ('business',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business', 'category', 'price', 'stock_qty', 'is_active', 'sort_order')
    list_filter = ('is_active', 'category', 'business__city')
    search_fields = ('name', 'description', 'sku', 'business__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('business', 'category', 'media')
    list_editable = ('is_active', 'sort_order')


@admin.register(ProductImportJob)
class ProductImportJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'status', 'total_rows', 'success_rows', 'error_rows', 'created_at', 'finished_at')
    list_filter = ('status', 'created_at', 'finished_at')
    search_fields = ('business__name',)
    readonly_fields = ('id', 'created_at', 'finished_at')
    autocomplete_fields = ('business', 'file_media')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'customer', 'city', 'status', 'payment_status', 'delivery_type', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'delivery_type', 'city', 'created_at')
    search_fields = ('business__name', 'customer__email', 'customer__phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('city', 'business', 'customer')
    inlines = (OrderItemInline,)
    date_hierarchy = 'created_at'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'name_snapshot', 'qty', 'price', 'total')
    search_fields = ('name_snapshot', 'product__name')
    readonly_fields = ('id',)
    autocomplete_fields = ('order', 'product')


@admin.register(BusinessAnalyticsDaily)
class BusinessAnalyticsDailyAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'day', 'views', 'orders_count', 'revenue_total', 'conversion_rate', 'avg_check')
    list_filter = ('day', 'business')
    search_fields = ('business__name',)
    autocomplete_fields = ('business',)
    date_hierarchy = 'day'
