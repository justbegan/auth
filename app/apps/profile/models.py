import uuid
from decimal import Decimal

from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from apps.user.models import CustomUser


class MediaFile(models.Model):
    id = models.UUIDField("ID файла", primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(CustomUser, verbose_name="Владелец", on_delete=models.SET_NULL, blank=True, null=True)
    bucket = models.CharField("S3 bucket", max_length=120)
    object_key = models.TextField("S3 key")
    url = models.TextField("CDN/public URL", blank=True, null=True)
    mime_type = models.CharField("MIME", max_length=120, blank=True, null=True)
    size_bytes = models.BigIntegerField("Размер", blank=True, null=True)
    width = models.IntegerField("Ширина", blank=True, null=True)
    height = models.IntegerField("Высота", blank=True, null=True)
    status = models.CharField("Статус", max_length=24, default="active")
    created_at = models.DateTimeField("Дата загрузки", auto_now_add=True)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.object_key


class City(models.Model):
    id = models.UUIDField("ID города", primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField("URL-ключ города", max_length=80, unique=True)
    name = models.CharField("Название", max_length=160)
    region = models.CharField("Регион", max_length=160, blank=True, null=True)
    timezone = models.CharField("Таймзона", max_length=64)
    point = models.PointField("Центр карты", srid=4326, blank=True, null=True)
    is_active = models.BooleanField("Доступность города", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            GistIndex(fields=['point']),
        ]

    def __str__(self):
        return self.name

    @property
    def lat(self):
        if not self.point:
            return None
        return Decimal(str(self.point.y))

    @property
    def lng(self):
        if not self.point:
            return None
        return Decimal(str(self.point.x))


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, verbose_name="Пользователь")
    first_name = models.CharField("Имя", max_length=100, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=100, blank=True, null=True)
    avatar_media = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Аватар")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Город")
    metadata = models.JSONField("Доп. настройки", default=dict)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return str(self.user)


class Notification(models.Model):
    id = models.UUIDField("ID уведомления", primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications",
                             verbose_name="Получатель")
    type = models.CharField("Тип события", max_length=64)
    title = models.CharField("Заголовок", max_length=200)
    body = models.TextField("Текст", blank=True, null=True)
    entity_type = models.CharField("Связанная сущность", max_length=64, blank=True, null=True)
    entity_id = models.UUIDField("ID сущности", blank=True, null=True)
    read_at = models.DateTimeField("Прочитано", blank=True, null=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    id = models.UUIDField("ID события", primary_key=True, default=uuid.uuid4, editable=False)
    actor_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="audit_logs", verbose_name="Кто совершил действие"
    )
    action = models.CharField("Действие", max_length=120)
    entity_type = models.CharField("Тип сущности", max_length=80)
    entity_id = models.UUIDField("ID сущности", blank=True, null=True)
    before_data = models.JSONField("До изменения", blank=True, null=True)
    after_data = models.JSONField("После изменения", blank=True, null=True)
    ip_address = models.GenericIPAddressField("ip", blank=True, null=True)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
        indexes = [
            models.Index(fields=['actor_user', 'created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f'{self.action}: {self.entity_type}'
