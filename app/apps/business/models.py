import uuid
from decimal import Decimal

from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex


class Business(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        PENDING = 'pending', 'На модерации'
        ACTIVE = 'active', 'Активен'
        REJECTED = 'rejected', 'Отклонен'
        BLOCKED = 'blocked', 'Заблокирован'

    id = models.UUIDField('ID бизнеса', primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        'user.CustomUser', verbose_name='Владелец', on_delete=models.CASCADE, related_name='businesses'
    )
    city = models.ForeignKey(
        'profile.City', verbose_name='Город', on_delete=models.PROTECT, related_name='businesses'
    )
    category = models.ForeignKey(
        'admin_panel.Category', verbose_name='Категория', on_delete=models.SET_NULL, blank=True, null=True
    )
    name = models.CharField('Название', max_length=200)
    slug = models.CharField('URL-ключ', max_length=160)
    description = models.TextField('Описание', blank=True, null=True)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.DRAFT)
    phone = models.CharField('Телефон', max_length=32, blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    website = models.TextField('Сайт', blank=True, null=True)
    rating = models.DecimalField('Рейтинг', max_digits=2, decimal_places=1, default=0)
    reviews_count = models.IntegerField('Количество отзывов', default=0)
    logo_media = models.ForeignKey(
        'profile.MediaFile', verbose_name='Логотип',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='business_logos'
    )
    cover_media = models.ForeignKey(
        'profile.MediaFile', verbose_name='Обложка',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='business_covers'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Бизнес'
        verbose_name_plural = 'Бизнесы'
        indexes = [
            models.Index(fields=['city', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['owner']),
            models.Index(fields=['slug']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['city', 'slug'], name='unique_business_city_slug'),
        ]

    def __str__(self):
        return self.name


class BusinessLocation(models.Model):
    id = models.UUIDField('ID адреса', primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, verbose_name='Бизнес', on_delete=models.CASCADE, related_name='locations')
    address = models.TextField('Адрес')
    district = models.CharField('Район', max_length=120, blank=True, null=True)
    point = models.PointField('Координаты', srid=4326, blank=True, null=True)
    geohash = models.CharField('Геоиндекс', max_length=32, blank=True, null=True)
    is_main = models.BooleanField('Основной адрес', default=True)

    class Meta:
        verbose_name = 'Адрес бизнеса'
        verbose_name_plural = 'Адреса бизнеса'
        indexes = [
            models.Index(fields=['business']),
            models.Index(fields=['geohash']),
            GistIndex(fields=['point']),
        ]

    def __str__(self):
        return self.address

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


class BusinessWorkingHours(models.Model):
    id = models.UUIDField('ID часов работы', primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, verbose_name='Бизнес', on_delete=models.CASCADE, related_name='working_hours'
    )
    day_of_week = models.SmallIntegerField('День недели')
    open_time = models.TimeField('Время открытия', blank=True, null=True)
    close_time = models.TimeField('Время закрытия', blank=True, null=True)
    is_closed = models.BooleanField('Закрыто', default=False)

    class Meta:
        verbose_name = 'Часы работы'
        verbose_name_plural = 'Часы работы'
        ordering = ['day_of_week']
        constraints = [
            models.UniqueConstraint(fields=['business', 'day_of_week'], name='unique_business_working_day'),
        ]

    def __str__(self):
        return f'{self.business}: {self.day_of_week}'


class Product(models.Model):
    id = models.UUIDField('ID товара', primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, verbose_name='Бизнес', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(
        'admin_panel.Category', verbose_name='Категория', on_delete=models.SET_NULL, blank=True, null=True
    )
    name = models.CharField('Название', max_length=220)
    description = models.TextField('Описание', blank=True, null=True)
    sku = models.CharField('Артикул', max_length=80, blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=14, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=14, decimal_places=2, blank=True, null=True)
    stock_qty = models.IntegerField('Остаток', default=0)
    is_active = models.BooleanField('Активен', default=True)
    sort_order = models.IntegerField('Порядок сортировки', default=0)
    media = models.ForeignKey(
        'profile.MediaFile', verbose_name='Главное фото', on_delete=models.SET_NULL, blank=True, null=True
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['business', 'is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.name


class ProductImportJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'queued', 'В очереди'
        PROCESSING = 'processing', 'В обработке'
        DONE = 'done', 'Готово'
        FAILED = 'failed', 'Ошибка'

    id = models.UUIDField('ID импорта', primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, verbose_name='Бизнес', on_delete=models.CASCADE, related_name='product_import_jobs'
    )
    file_media = models.ForeignKey(
        'profile.MediaFile', verbose_name='Файл импорта', on_delete=models.SET_NULL, blank=True, null=True
    )
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.QUEUED)
    total_rows = models.IntegerField('Всего строк', default=0)
    success_rows = models.IntegerField('Успешных строк', default=0)
    error_rows = models.IntegerField('Ошибочных строк', default=0)
    errors = models.JSONField('Ошибки', default=list)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    finished_at = models.DateTimeField('Дата завершения', blank=True, null=True)

    class Meta:
        verbose_name = 'Импорт товаров'
        verbose_name_plural = 'Импорты товаров'
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.business}: {self.status}'


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Создан'
        CONFIRMED = 'confirmed', 'Подтвержден'
        WORKING = 'working', 'В работе'
        READY = 'ready', 'Готов'
        DELIVERING = 'delivering', 'Доставляется'
        COMPLETED = 'completed', 'Завершен'
        CANCELLED = 'cancelled', 'Отменен'

    class DeliveryType(models.TextChoices):
        DELIVERY = 'delivery', 'Доставка'
        PICKUP = 'pickup', 'Самовывоз'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        PAID = 'paid', 'Оплачен'
        REFUNDED = 'refunded', 'Возвращен'
        FAILED = 'failed', 'Ошибка'

    id = models.UUIDField('ID заказа', primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.PROTECT, related_name='orders')
    business = models.ForeignKey(Business, verbose_name='Бизнес', on_delete=models.PROTECT, related_name='orders')
    customer = models.ForeignKey(
        'user.CustomUser', verbose_name='Покупатель', on_delete=models.PROTECT, related_name='orders'
    )
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.CREATED)
    delivery_type = models.CharField('Тип доставки', max_length=24, choices=DeliveryType.choices)
    payment_status = models.CharField(
        'Статус оплаты', max_length=24, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    subtotal = models.DecimalField('Сумма товаров', max_digits=14, decimal_places=2)
    delivery_fee = models.DecimalField('Стоимость доставки', max_digits=14, decimal_places=2, default=0)
    discount_total = models.DecimalField('Сумма скидки', max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField('Итоговая сумма', max_digits=14, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3, default='RUB')
    address = models.JSONField('Адрес доставки', blank=True, null=True)
    scheduled_at = models.DateTimeField('Запланированное время', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['business', 'status']),
            models.Index(fields=['city', 'status']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    id = models.UUIDField('ID позиции', primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.SET_NULL, blank=True, null=True)
    name_snapshot = models.CharField('Название на момент заказа', max_length=220)
    qty = models.DecimalField('Количество', max_digits=10, decimal_places=3)
    price = models.DecimalField('Цена', max_digits=14, decimal_places=2)
    total = models.DecimalField('Сумма', max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return self.name_snapshot


class BusinessAnalyticsDaily(models.Model):
    business = models.ForeignKey(
        Business, verbose_name='Бизнес', on_delete=models.CASCADE, related_name='analytics_daily'
    )
    day = models.DateField('День')
    views = models.IntegerField('Просмотры', default=0)
    orders_count = models.IntegerField('Количество заказов', default=0)
    revenue_total = models.DecimalField('Выручка', max_digits=14, decimal_places=2, default=0)
    conversion_rate = models.DecimalField('Конверсия', max_digits=5, decimal_places=2, default=0)
    avg_check = models.DecimalField('Средний чек', max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Аналитика бизнеса за день'
        verbose_name_plural = 'Аналитика бизнеса за дни'
        indexes = [
            models.Index(fields=['business', 'day']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['business', 'day'], name='unique_business_analytics_day'),
        ]

    def __str__(self):
        return f'{self.business}: {self.day}'
