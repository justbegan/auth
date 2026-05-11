from django.contrib import admin

from apps.admin_panel.models import AdCampaign, AdminStatsDaily, Category, ModerationCase, ReviewReport, Tariff


@admin.register(AdminStatsDaily)
class AdminStatsDailyAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'city', 'day', 'users_count', 'businesses_count',
        'orders_count', 'revenue_total', 'ads_revenue_total', 'created_at',
    )
    list_filter = ('city', 'day', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('city',)
    date_hierarchy = 'day'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'parent', 'slug', 'name', 'sort_order', 'is_active')
    list_filter = ('section', 'is_active', 'parent')
    search_fields = ('slug', 'name')
    readonly_fields = ('id',)
    autocomplete_fields = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('sort_order', 'is_active')


@admin.register(ModerationCase)
class ModerationCaseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'entity_type', 'entity_id', 'status', 'submitted_by',
        'assigned_to', 'decided_by', 'decided_at', 'created_at',
    )
    list_filter = ('entity_type', 'status', 'created_at', 'decided_at')
    search_fields = ('entity_type', 'reason', 'submitted_by__email', 'assigned_to__email')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('submitted_by', 'assigned_to', 'decided_by')
    list_editable = ('status',)
    date_hierarchy = 'created_at'


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'reporter', 'reason', 'status', 'resolved_by', 'resolved_at', 'created_at')
    list_filter = ('status', 'reason', 'created_at', 'resolved_at')
    search_fields = ('review__text', 'reporter__email', 'comment')
    readonly_fields = ('id', 'created_at')
    autocomplete_fields = ('review', 'reporter', 'resolved_by')
    list_editable = ('status',)


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'business', 'city', 'placement', 'status',
        'budget_total', 'budget_spent', 'views_count', 'clicks_count',
        'starts_at', 'ends_at',
    )
    list_filter = ('placement', 'status', 'city', 'starts_at', 'ends_at')
    search_fields = ('title', 'business__name')
    readonly_fields = ('id', 'views_count', 'clicks_count', 'created_at')
    autocomplete_fields = ('business', 'city')
    list_editable = ('status',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'target', 'price_month', 'is_active')
    list_filter = ('target', 'is_active', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('id', 'created_at')
    list_editable = ('price_month', 'is_active')
