import uuid

from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Review(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = 'published', 'Опубликован'
        HIDDEN = 'hidden', 'Скрыт'
        DELETED = 'deleted', 'Удален'
        PENDING = 'pending', 'На модерации'

    id = models.UUIDField('ID отзыва', primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        'business.Business', verbose_name='Бизнес', on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey('user.CustomUser', verbose_name='Автор', on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(
        'business.Order', verbose_name='Заказ',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='reviews'
    )
    rating = models.SmallIntegerField('Оценка')
    text = models.TextField('Текст', blank=True, null=True)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.PUBLISHED)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.business}: {self.rating}'


class FeedPost(models.Model):
    class Type(models.TextChoices):
        PROMO = 'promo', 'Акция'
        NEWS = 'news', 'Новость'
        EVENT = 'event', 'Событие'
        POST = 'post', 'Пост'

    class Status(models.TextChoices):
        PUBLISHED = 'published', 'Опубликован'
        HIDDEN = 'hidden', 'Скрыт'
        DELETED = 'deleted', 'Удален'
        PENDING = 'pending', 'На модерации'

    id = models.UUIDField('ID поста', primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.CASCADE, related_name='feed_posts')
    business = models.ForeignKey(
        'business.Business', verbose_name='Бизнес', on_delete=models.SET_NULL, blank=True, null=True
    )
    author_user = models.ForeignKey(
        'user.CustomUser', verbose_name='Автор', on_delete=models.CASCADE, related_name='feed_posts'
    )
    type = models.CharField('Тип', max_length=24, choices=Type.choices)
    title = models.CharField('Заголовок', max_length=240, blank=True, null=True)
    body = models.TextField('Текст')
    tags = models.JSONField('Теги', default=list)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.PUBLISHED)
    event_at = models.DateTimeField('Дата события', blank=True, null=True)
    event_location = models.TextField('Место события', blank=True, null=True)
    promo_price = models.DecimalField('Цена акции', max_digits=14, decimal_places=2, blank=True, null=True)
    promo_old_price = models.DecimalField('Старая цена акции', max_digits=14, decimal_places=2, blank=True, null=True)
    published_at = models.DateTimeField('Дата публикации', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Пост ленты'
        verbose_name_plural = 'Посты ленты'
        indexes = [
            models.Index(fields=['city', 'status', 'published_at']),
            models.Index(fields=['type']),
            models.Index(fields=['business']),
            GinIndex(fields=['tags']),
        ]

    def __str__(self):
        return self.title or self.body[:80]


class FeedPostMedia(models.Model):
    id = models.UUIDField('ID медиа поста', primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(FeedPost, verbose_name='Пост', on_delete=models.CASCADE, related_name='media')
    media = models.ForeignKey('profile.MediaFile', verbose_name='Медиа', on_delete=models.CASCADE)
    sort_order = models.IntegerField('Порядок сортировки', default=0)

    class Meta:
        verbose_name = 'Медиа поста'
        verbose_name_plural = 'Медиа постов'
        ordering = ['sort_order']


class FeedComment(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = 'published', 'Опубликован'
        HIDDEN = 'hidden', 'Скрыт'
        DELETED = 'deleted', 'Удален'

    id = models.UUIDField('ID комментария', primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(FeedPost, verbose_name='Пост', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        'user.CustomUser', verbose_name='Автор', on_delete=models.CASCADE, related_name='feed_comments'
    )
    parent = models.ForeignKey(
        'self', verbose_name='Родительский комментарий',
        on_delete=models.CASCADE, blank=True, null=True, related_name='children'
    )
    body = models.TextField('Текст')
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.PUBLISHED)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий ленты'
        verbose_name_plural = 'Комментарии ленты'
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.body[:80]


class FeedReaction(models.Model):
    id = models.UUIDField('ID реакции', primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(FeedPost, verbose_name='Пост', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(
        'user.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE, related_name='feed_reactions'
    )
    reaction = models.CharField('Тип реакции', max_length=24, default='like')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Реакция на пост'
        verbose_name_plural = 'Реакции на посты'
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['post', 'user', 'reaction'], name='unique_feed_reaction'),
        ]


class Follow(models.Model):
    id = models.UUIDField('ID подписки', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'user.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE, related_name='follows'
    )
    business = models.ForeignKey(
        'business.Business', verbose_name='Бизнес', on_delete=models.CASCADE, related_name='followers'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'business'], name='unique_user_business_follow'),
        ]


class Story(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        HIDDEN = 'hidden', 'Скрыта'
        EXPIRED = 'expired', 'Истекла'

    id = models.UUIDField('ID сторис', primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.CASCADE, related_name='stories')
    business = models.ForeignKey(
        'business.Business', verbose_name='Бизнес', on_delete=models.CASCADE, related_name='stories'
    )
    title = models.CharField('Название', max_length=180, blank=True, null=True)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.ACTIVE)
    expires_at = models.DateTimeField('Дата истечения')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Сторис'
        verbose_name_plural = 'Сторис'
        indexes = [
            models.Index(fields=['city', 'status', 'expires_at']),
            models.Index(fields=['business']),
        ]

    def __str__(self):
        return self.title or str(self.id)


class StorySlide(models.Model):
    id = models.UUIDField('ID слайда', primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, verbose_name='Сторис', on_delete=models.CASCADE, related_name='slides')
    media = models.ForeignKey('profile.MediaFile', verbose_name='Медиа', on_delete=models.CASCADE)
    caption = models.TextField('Подпись', blank=True, null=True)
    cta_label = models.CharField('Текст кнопки', max_length=80, blank=True, null=True)
    cta_url = models.TextField('URL кнопки', blank=True, null=True)
    sort_order = models.IntegerField('Порядок сортировки', default=0)

    class Meta:
        verbose_name = 'Слайд сторис'
        verbose_name_plural = 'Слайды сторис'
        ordering = ['sort_order']


class ChatConversation(models.Model):
    class Kind(models.TextChoices):
        ORDER = 'order', 'Заказ'
        BUSINESS = 'business', 'Бизнес'
        SUPPORT = 'support', 'Поддержка'
        BOARD = 'board', 'Объявление'

    id = models.UUIDField('ID чата', primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(
        'profile.City', verbose_name='Город', on_delete=models.CASCADE, related_name='chat_conversations'
    )
    kind = models.CharField('Тип чата', max_length=24, choices=Kind.choices)
    business = models.ForeignKey(
        'business.Business', verbose_name='Бизнес', on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.ForeignKey('business.Order', verbose_name='Заказ', on_delete=models.SET_NULL, blank=True, null=True)
    listing = models.ForeignKey(
        'board.BoardListing', verbose_name='Объявление', on_delete=models.SET_NULL, blank=True, null=True
    )
    buyer = models.ForeignKey(
        'user.CustomUser', verbose_name='Покупатель',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='buyer_chats'
    )
    seller = models.ForeignKey(
        'user.CustomUser', verbose_name='Продавец',
        on_delete=models.SET_NULL, blank=True, null=True, related_name='seller_chats'
    )
    last_message_at = models.DateTimeField('Дата последнего сообщения', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        indexes = [
            models.Index(fields=['buyer', 'last_message_at']),
            models.Index(fields=['seller', 'last_message_at']),
            models.Index(fields=['business']),
            models.Index(fields=['listing']),
        ]

    def __str__(self):
        return f'{self.kind}: {self.id}'


class ChatMessage(models.Model):
    id = models.UUIDField('ID сообщения', primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ChatConversation, verbose_name='Чат', on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        'user.CustomUser', verbose_name='Отправитель', on_delete=models.CASCADE, related_name='chat_messages'
    )
    body = models.TextField('Текст', blank=True, null=True)
    media = models.ForeignKey(
        'profile.MediaFile', verbose_name='Медиа', on_delete=models.SET_NULL, blank=True, null=True
    )
    read_at = models.DateTimeField('Дата прочтения', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return self.body or str(self.id)


class AIRequest(models.Model):
    id = models.UUIDField('ID AI-запроса', primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'user.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE, related_name='ai_requests'
    )
    city = models.ForeignKey('profile.City', verbose_name='Город', on_delete=models.CASCADE, related_name='ai_requests')
    prompt = models.TextField('Запрос')
    context = models.JSONField('Контекст', default=dict)
    response = models.JSONField('Ответ', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'AI-запрос'
        verbose_name_plural = 'AI-запросы'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return self.prompt[:80]
