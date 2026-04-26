from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Role(models.Model):
    title = models.TextField("Название")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class CustomUser(AbstractUser):
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    email = models.EmailField("эл. почта", unique=True)
    patronymic = models.CharField("Отчество", max_length=50, blank=True, null=True)
    last_activity = models.DateTimeField("Последняя активность", blank=True, null=True)
    history = HistoricalRecords("История")
    phone = PhoneNumberField(unique=True, region="RU", verbose_name="Телефон", blank=False, null=True)
    role = models.ForeignKey(Role, verbose_name="Роль", on_delete=models.PROTECT, null=True, blank=False)

    def __str__(self):
        return self.username

    def get_full_name_v2(self):
        full_name = "%s %s %s" % (self.last_name, self.first_name, self.patronymic)
        return full_name.strip()
