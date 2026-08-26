from django.db import models

from apps.addresses.models import Unit


class AccountStatus(models.TextChoices):
    ACTIVE = "active", "Открыт"
    CLOSED = "closed", "Закрыт"


class PersonalAccount(models.Model):
    """Лицевой счёт — центральная сущность биллинга.

    Все начисления, показания приборов учёта и наниматели привязываются
    к лицевому счёту, а не напрямую к помещению — это позволяет вести
    историю при смене нанимателя без потери начислений за прошлые периоды.
    """

    number = models.CharField("Номер лицевого счёта", max_length=20, unique=True)
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name="accounts", verbose_name="Помещение"
    )
    status = models.CharField(
        "Статус", max_length=10, choices=AccountStatus.choices, default=AccountStatus.ACTIVE
    )
    registered_count = models.PositiveSmallIntegerField(
        "Кол-во зарегистрированных лиц", default=0,
        help_text="Используется для начислений по тарифу «руб/чел»",
    )
    opened_at = models.DateField("Дата открытия")
    closed_at = models.DateField("Дата закрытия", null=True, blank=True)
    notes = models.TextField("Примечания", blank=True)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Лицевой счёт"
        verbose_name_plural = "Лицевые счета"
        ordering = ("number",)
        indexes = [models.Index(fields=["number"]), models.Index(fields=["status"])]

    def __str__(self):
        return f"ЛС №{self.number} ({self.unit})"

    @property
    def current_responsible(self):
        """Текущий ответственный наниматель (последнее назначение без даты окончания)."""
        assignment = (
            self.tenant_assignments.filter(end_date__isnull=True)
            .order_by("-start_date")
            .select_related("tenant")
            .first()
        )
        return assignment.tenant if assignment else None
