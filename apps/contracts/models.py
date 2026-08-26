from datetime import date

from django.conf import settings
from django.db import models

from apps.accounts.models import PersonalAccount


class Contract(models.Model):
    """Договор (найма/аренды/обслуживания), привязанный к лицевому счёту."""

    account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Лицевой счёт",
    )
    number = models.CharField("Номер договора", max_length=50)
    signed_date = models.DateField("Дата заключения")
    end_date = models.DateField("Дата окончания", null=True, blank=True)

    responsible_employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="responsible_contracts",
        verbose_name="Ответственные сотрудники",
        blank=True,
        help_text="Получат уведомление за месяц до окончания договора",
    )

    expiry_notified_at = models.DateTimeField(
        "Уведомление отправлено", null=True, blank=True, editable=False
    )

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
        unique_together = ("account", "number")
        ordering = ("-signed_date",)
        indexes = [models.Index(fields=["end_date"])]

    def __str__(self):
        return f"Договор №{self.number} (ЛС {self.account.number})"

    @property
    def is_active(self):
        return self.end_date is None or self.end_date >= date.today()
