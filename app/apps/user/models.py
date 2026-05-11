from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class CustomUser(AbstractUser):
    class AccountType(models.TextChoices):
        USER = 'user', 'Пользователь'
        BUSINESS = 'business', 'Бизнес'
        ADMIN = 'admin', 'Администратор'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активен'
        BLOCKED = 'blocked', 'Заблокирован'
        DELETED = 'deleted', 'Удален'

    id = models.UUIDField('ID пользователя', primary_key=True, default=uuid.uuid4, editable=False)
    phone = PhoneNumberField(unique=True, region="RU", verbose_name="Телефон", blank=False, null=True)
    email = models.EmailField("эл. почта", unique=True)
    account_type = models.CharField('Тип', max_length=24, choices=AccountType.choices, default=AccountType.USER)
    status = models.CharField('Статус', max_length=24, choices=Status.choices, default=Status.ACTIVE)
    last_activity = models.DateTimeField("Последняя активность", blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    history = HistoricalRecords("История")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['account_type', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return self.email or self.username

    def get_full_name_v2(self):
        full_name = "%s %s" % (self.last_name, self.first_name)
        return full_name.strip()
