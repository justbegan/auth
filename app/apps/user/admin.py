from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin):
    search_fields = ("first_name", "last_name", "email", "phone")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Персональная информация", {"fields": (
            "first_name", "last_name"
        )}),
        ("Рабочие данные", {"fields": ("last_activity", "phone", "account_type", "status")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    ordering = ['-id']
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "first_name", "last_name",
                "is_staff", "is_active", "phone",
            ),
        }),
    )
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'phone')
