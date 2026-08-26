from django.db import models

from apps.accounts.models import PersonalAccount


class Tenant(models.Model):
    """Наниматель / физическое лицо, ответственное за лицевой счёт."""

    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    middle_name = models.CharField("Отчество", max_length=100, blank=True)

    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)

    passport_series = models.CharField("Серия паспорта", max_length=10, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, blank=True)
    passport_issued_by = models.CharField("Кем выдан", max_length=255, blank=True)
    passport_issued_date = models.DateField("Дата выдачи", null=True, blank=True)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Наниматель"
        verbose_name_plural = "Наниматели"
        ordering = ("last_name", "first_name")

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)


class TenantAccountAssignment(models.Model):
    """История назначения нанимателей ответственными по лицевому счёту.

    На одном лицевом счёте может быть несколько нанимателей одновременно
    (is_primary отмечает основного плательщика); при смене ответственного
    старая запись закрывается датой end_date, а не удаляется.
    """

    account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.CASCADE,
        related_name="tenant_assignments",
        verbose_name="Лицевой счёт",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="account_assignments",
        verbose_name="Наниматель",
    )
    is_primary = models.BooleanField("Основной плательщик", default=True)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", null=True, blank=True)
    reason = models.CharField(
        "Основание", max_length=255, blank=True,
        help_text="Например: договор найма №..., смена собственника и т.п.",
    )

    class Meta:
        verbose_name = "Назначение нанимателя"
        verbose_name_plural = "История нанимателей по лицевым счетам"
        ordering = ("-start_date",)
        indexes = [models.Index(fields=["account", "end_date"])]

    def __str__(self):
        return f"{self.tenant} — ЛС №{self.account.number} (с {self.start_date})"
