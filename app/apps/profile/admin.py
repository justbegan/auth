from django.contrib import admin
from .models import City, UserProfile, MediaFile, Notification, AuditLog


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "name", "region", "timezone", "is_active", "created_at")
    search_fields = ("name", "slug", "region")
    list_filter = ("is_active", "region", "timezone")
    readonly_fields = ("id", "created_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "city")
    search_fields = ("user__username", "first_name", "last_name")
    list_filter = ("city",)
    readonly_fields = ("user",)


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "bucket", "object_key", "mime_type", "size_bytes", "status", "created_at")
    search_fields = ("object_key", "bucket", "mime_type")
    list_filter = ("status", "bucket", "mime_type")
    readonly_fields = ("id", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "title", "read_at", "created_at")
    search_fields = ("title", "type", "user__username")
    list_filter = ("type", "read_at")
    readonly_fields = ("id", "created_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor_user", "action", "entity_type", "entity_id", "ip_address", "created_at")
    search_fields = ("action", "entity_type", "actor_user__username", "ip_address")
    list_filter = ("entity_type", "action", "created_at")
    readonly_fields = ("id", "created_at")
