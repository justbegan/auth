# core/management/commands/create_app.py

import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Создание приложения с кастомной структурой"

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str)

    def handle(self, *args, **options):
        app_name = options['app_name']
        base_dir = settings.BASE_DIR

        app_path = os.path.join(base_dir, "apps", app_name)
        self.add_to_installed_apps(app_name)
        self.add_to_main_urls(app_name)

        if os.path.exists(app_path):
            self.stdout.write(self.style.ERROR(f'Приложение {app_name} уже существует'))
            return

        if not app_name.isidentifier():
            raise ValueError("Некорректное имя приложения")

        self.create_structure(app_path, app_name)
        self.stdout.write(self.style.SUCCESS(f'Приложение {app_name} создано'))

    def create_structure(self, app_path, app_name):
        os.makedirs(app_path, exist_ok=True)

        api_path = os.path.join(app_path, 'api')
        v1_path = os.path.join(api_path, 'v1')

        os.makedirs(v1_path, exist_ok=True)

        root_files = {
            '__init__.py': '',
            'models.py': self.models_template(),
            'admin.py': self.admin_template(),
            'apps.py': self.apps_template(app_name),
            'tests.py': '',
            'services.py': '',
        }

        for filename, content in root_files.items():
            with open(os.path.join(app_path, filename), 'w', encoding='utf-8') as f:
                f.write(content)

        v1_files = {
            '__init__.py': '',
            'views.py': self.views_template(),
            'serializers.py': self.serializers_template(),
            'urls.py': self.urls_template(app_name),
            'services.py': '',
        }

        for filename, content in v1_files.items():
            with open(os.path.join(v1_path, filename), 'w', encoding='utf-8') as f:
                f.write(content)

    def models_template(self):
        return """from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
"""

    def serializers_template(self):
        return """# from rest_framework import serializers
"""

    def views_template(self):
        return """from rest_framework.views import (APIView, Request, Response)
from drf_spectacular.utils import extend_schema


@extend_schema(
    methods=["GET"],
    summary="Приветствие",
)
class HelloWorldMain(APIView):
    def get(self, request: Request) -> Response:
        return Response({'hello': 'world'})


@extend_schema(
    methods=["GET"],
    summary="Приветствие с параметром",
)
class HelloWorldDetails(APIView):
    def get(self, request: Request, pk: int) -> Response:
        return Response({'hello': f'world {pk}'})
"""

    def urls_template(self, app_name):
        return """from django.urls import path
from . import views


urlpatterns = [
    path('main', views.HelloWorldMain.as_view(), name='main'),
    path('details/<int:pk>', views.HelloWorldDetails.as_view(), name='details'),
]
"""

    def apps_template(self, app_name):
        class_name = app_name.capitalize()

        return f"""from django.apps import AppConfig


class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
"""

    def admin_template(self):
        return """# from django.contrib import admin


# @admin.register(App)
# class App_admin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'created_at', 'updated_at')
"""

    def add_to_installed_apps(self, app_name):
        settings_path = settings.BASE_DIR / 'main_app' / 'settings.py'

        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_line = f"    'apps.{app_name}'"

        content = content.replace(
            '# Пользовательские приложения',
            f'# Пользовательские приложения\n{new_line},'
        )

        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def add_to_main_urls(self, app_name):
        settings_path = settings.BASE_DIR / 'main_app' / 'urls.py'

        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_line = f"    path(f'{{START_SYMBOL}}{app_name}/v1/', include('apps.{app_name}.api.v1.urls'))"

        content = content.replace(
            '# Пользовательские роуты',
            f'# Пользовательские роуты\n{new_line},'
        )

        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
