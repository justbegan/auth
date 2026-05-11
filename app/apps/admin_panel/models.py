import uuid

from django.db import models


class AdminStatsDaily(models.Model):
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.SET_NULL, blank=True, null=True)
    day = models.DateField('День')
    users_count = models.IntegerField('Количество пользователей', default=0)
    businesses_count = models.IntegerField('Количество бизнесов', default=0)
    orders_count = models.IntegerField('Количество заказов', default=0)
    revenue_total = models.DecimalField('Общая выручка', max_digits=14, decimal_places=2, default=0)
    ads_revenue_total = models.DecimalField('Выручка рекламы', max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Статистика админки за день'
        verbose_name_plural = 'Статистика админки за дни'
        indexes = [
            models.Index(fields=['city', 'day']),
            models.Index(fields=['day']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['city', 'day'], name='unique_admin_stats_city_day'),
        ]

    def __str__(self):
        return f'{self.city or "all"} {self.day}'


class Category(models.Model):
    class Section(models.TextChoices):
        CITY = 'city', 'Город'
        BUSINESS = 'business', 'Бизнес'
        BOARD = 'board', 'Объявления'

    id = models.UUIDField('ID категории', primary_key=True, default=uuid.uuid4, editable=False)
    section = models.CharField('Раздел', max_length=24, choices=Section.choices)
    parent = models.ForeignKey(
        'self', verbose_name='Родительская категория',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='children'
    )
    slug = models.CharField('URL-ключ', max_length=120)
    name = models.CharField('Название', max_length=160)
    icon = models.CharField('Иконка', max_length=80, blank=True, null=True)
    color = models.CharField('Цвет', max_length=16, blank=True, null=True)
    sort_order = models.IntegerField('Порядок сортировки', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['section', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['section', 'parent']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['section', 'slug'], name='unique_category_section_slug'),
        ]

    def __str__(self):
        return f'{self.section}: {self.name}'


class ModerationCase(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На рассмотрении'
        APPROVED = 'approved', 'Одобрено'
        REJECTED = 'rejected', 'Отклонено'

    id = models.UUIDField('ID кейса', primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField('Тип сущности', max_length=64)
    entity_id = models.UUIDField('ID сущности')
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField('Причина решения', blank=True, null=True)
    submitted_by = models.ForeignKey(
        'user.CustomUser', verbose_name='Автор заявки',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='submitted_cases'
    )
    assigned_to = models.ForeignKey(
        'user.CustomUser', verbose_name='Назначенный модератор',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_cases'
    )
    decided_by = models.ForeignKey(
        'user.CustomUser', verbose_name='Принял решение',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='decided_cases'
    )
    decided_at = models.DateTimeField('Дата решения', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Кейс модерации'
        verbose_name_plural = 'Кейсы модерации'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.entity_type} {self.status}'


class ReviewReport(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Новая'
        RESOLVED = 'resolved', 'Решена'
        REJECTED = 'rejected', 'Отклонена'

    id = models.UUIDField('ID жалобы', primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey('city.Review', verbose_name='Отзыв', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(
        'user.CustomUser', verbose_name='Автор жалобы', on_delete=models.CASCADE, related_name='review_reports'
    )
    reason = models.CharField('Причина', max_length=80)
    comment = models.TextField('Комментарий', blank=True, null=True)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.PENDING)
    resolved_by = models.ForeignKey(
        'user.CustomUser', verbose_name='Обработал',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='resolved_review_reports'
    )
    resolved_at = models.DateTimeField('Дата обработки', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Жалоба на отзыв'
        verbose_name_plural = 'Жалобы на отзывы'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['review']),
        ]

    def __str__(self):
        return f'{self.review_id}: {self.status}'


class AdCampaign(models.Model):
    class Placement(models.TextChoices):
        FEED = 'feed', 'Лента'
        SEARCH = 'search', 'Поиск'
        MAP = 'map', 'Карта'
        BOARD = 'board', 'Объявления'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        ACTIVE = 'active', 'Активна'
        PAUSED = 'paused', 'На паузе'
        FINISHED = 'finished', 'Завершена'

    id = models.UUIDField('ID кампании', primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        'business.Business', verbose_name='Бизнес', on_delete=models.CASCADE, related_name='ad_campaigns'
    )
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.SET_NULL, blank=True, null=True)
    placement = models.CharField('Размещение', max_length=40, choices=Placement.choices)
    title = models.CharField('Название', max_length=200)
    budget_total = models.DecimalField('Общий бюджет', max_digits=14, decimal_places=2)
    budget_spent = models.DecimalField('Потраченный бюджет', max_digits=14, decimal_places=2, default=0)
    views_count = models.IntegerField('Количество показов', default=0)
    clicks_count = models.IntegerField('Количество кликов', default=0)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.DRAFT)
    starts_at = models.DateTimeField('Дата начала', blank=True, null=True)
    ends_at = models.DateTimeField('Дата завершения', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Рекламная кампания'
        verbose_name_plural = 'Рекламные кампании'
        indexes = [
            models.Index(fields=['status', 'placement']),
            models.Index(fields=['business', 'city']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]

    def __str__(self):
        return self.title


class Tariff(models.Model):
    class Target(models.TextChoices):
        BUSINESS = 'business', 'Бизнес'
        SELLER = 'seller', 'Продавец'
        USER = 'user', 'Пользователь'

    id = models.UUIDField('ID тарифа', primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField('Код тарифа', max_length=80, unique=True)
    name = models.CharField('Название', max_length=160)
    target = models.CharField('Целевая аудитория', max_length=24, choices=Target.choices)
    price_month = models.DecimalField('Цена за месяц', max_digits=14, decimal_places=2, default=0)
    features = models.JSONField('Возможности', default=list)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        indexes = [
            models.Index(fields=['target', 'is_active']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name
