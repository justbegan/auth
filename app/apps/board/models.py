import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from django.utils import timezone


class BoardListing(models.Model):
    class Condition(models.TextChoices):
        NEW = 'new', 'Новый'
        USED = 'used', 'Б/у'

    class SellerType(models.TextChoices):
        PRIVATE = 'private', 'Частное лицо'
        BUSINESS = 'business', 'Бизнес'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        REVIEW = 'review', 'На модерации'
        ACTIVE = 'active', 'Активно'
        PAUSED = 'paused', 'На паузе'
        SOLD = 'sold', 'Продано'
        REJECTED = 'rejected', 'Отклонено'
        DELETED = 'deleted', 'Удалено'

    id = models.UUIDField('ID объявления', primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.PROTECT, related_name='board_listings')
    seller = models.ForeignKey('user.CustomUser', verbose_name='Продавец', on_delete=models.CASCADE, related_name='board_listings')
    category = models.ForeignKey(
        'admin_panel.Category', verbose_name='Категория',
        on_delete=models.PROTECT, related_name='board_category_listings'
    )
    subcategory = models.ForeignKey(
        'admin_panel.Category', verbose_name='Подкатегория',
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name='board_subcategory_listings'
    )
    title = models.CharField('Название', max_length=240)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=14, decimal_places=2, blank=True, null=True)
    currency = models.CharField('Валюта', max_length=3, default='RUB')
    condition = models.CharField('Состояние', max_length=24, choices=Condition.choices, blank=True, null=True)
    seller_type = models.CharField('Тип продавца', max_length=24, choices=SellerType.choices)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.DRAFT)
    negotiable = models.BooleanField('Возможен торг', default=False)
    district = models.CharField('Район', max_length=120, blank=True, null=True)
    address = models.TextField('Адрес', blank=True, null=True)
    point = models.PointField('Координаты', srid=4326, blank=True, null=True)
    views_count = models.IntegerField('Количество просмотров', default=0)
    contacts_count = models.IntegerField('Количество обращений', default=0)
    favorites_count = models.IntegerField('Количество добавлений в избранное', default=0)
    boosted_until = models.DateTimeField('Поднято до', blank=True, null=True)
    expires_at = models.DateTimeField('Истекает', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        indexes = [
            models.Index(fields=['city', 'status', 'created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['subcategory']),
            models.Index(fields=['price']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['boosted_until']),
            GistIndex(fields=['point']),
        ]

    def __str__(self):
        return self.title

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

    def boost(self):
        self.boosted_until = timezone.now() + timedelta(days=7)
        self.save(update_fields=['boosted_until', 'updated_at'])


class BoardListingMedia(models.Model):
    id = models.UUIDField('ID медиа объявления', primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(BoardListing, verbose_name='Объявление', on_delete=models.CASCADE, related_name='media')
    media = models.ForeignKey('profile.MediaFile', verbose_name='Медиа', on_delete=models.CASCADE)
    sort_order = models.IntegerField('Порядок сортировки', default=0)

    class Meta:
        verbose_name = 'Медиа объявления'
        verbose_name_plural = 'Медиа объявлений'
        ordering = ['sort_order']


class BoardListingAttribute(models.Model):
    id = models.UUIDField('ID характеристики', primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(BoardListing, verbose_name='Объявление', on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField('Код характеристики', max_length=120)
    value_text = models.TextField('Текстовое значение', blank=True, null=True)
    value_num = models.DecimalField('Числовое значение', max_digits=14, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Характеристика объявления'
        verbose_name_plural = 'Характеристики объявлений'
        indexes = [
            models.Index(fields=['listing', 'key']),
        ]

    def __str__(self):
        return self.key


class BoardFavorite(models.Model):
    id = models.UUIDField('ID избранного', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('user.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE, related_name='board_favorites')
    listing = models.ForeignKey(BoardListing, verbose_name='Объявление', on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное объявление'
        verbose_name_plural = 'Избранные объявления'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'listing'], name='unique_board_favorite'),
        ]

    def __str__(self):
        return f'{self.user_id}: {self.listing_id}'


class BoardListingStatsDaily(models.Model):
    listing = models.ForeignKey(BoardListing, verbose_name='Объявление', on_delete=models.CASCADE, related_name='stats_daily')
    day = models.DateField('День')
    views = models.IntegerField('Просмотры', default=0)
    contacts = models.IntegerField('Обращения', default=0)
    favorites = models.IntegerField('Добавления в избранное', default=0)

    class Meta:
        verbose_name = 'Статистика объявления за день'
        verbose_name_plural = 'Статистика объявлений за дни'
        indexes = [
            models.Index(fields=['listing', 'day']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['listing', 'day'], name='unique_board_listing_stats_day'),
        ]

    def __str__(self):
        return f'{self.listing}: {self.day}'


class BoardReport(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Новая'
        RESOLVED = 'resolved', 'Решена'
        REJECTED = 'rejected', 'Отклонена'

    id = models.UUIDField('ID жалобы', primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(BoardListing, verbose_name='Объявление', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey('user.CustomUser', verbose_name='Автор жалобы', on_delete=models.CASCADE, related_name='board_reports')
    reason = models.CharField('Причина', max_length=80)
    comment = models.TextField('Комментарий', blank=True, null=True)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Жалоба на объявление'
        verbose_name_plural = 'Жалобы на объявления'
        indexes = [
            models.Index(fields=['listing']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.listing_id}: {self.status}'
