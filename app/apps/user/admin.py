from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin
from .models import CustomUser, Role
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin):
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": (
            "username", "first_name", "last_name", "patronymic"
        )}),
        ("Рабочие данные", {"fields": ("last_activity", "phone", "role")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    ordering = ['-id']
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "first_name", "last_name",
                "patronymic", "is_staff", "is_active", "phone",
            ),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass
