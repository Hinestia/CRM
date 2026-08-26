from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import PersonalAccount
from apps.services.models import Service


class Meter(models.Model):
    """Прибор учёта (счётчик) на лицевом счёте по конкретной услуге.

    Базовая версия модуля — хранит сам прибор и его показания.
    Массовый ввод показаний и расширенная поверка — задачи следующего этапа.
    """

    account = models.ForeignKey(
        PersonalAccount, on_delete=models.CASCADE, related_name="meters", verbose_name="Лицевой счёт"
    )
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="meters", verbose_name="Услуга",
        limit_choices_to={"calculation_method": "per_consumption"},
    )
    serial_number = models.CharField("Заводской номер", max_length=50)
    installed_date = models.DateField("Дата установки", null=True, blank=True)
    verification_date = models.DateField("Дата поверки", null=True, blank=True)
    next_verification_date = models.DateField("Следующая поверка", null=True, blank=True)
    is_active = models.BooleanField("В эксплуатации", default=True)

    class Meta:
        verbose_name = "Прибор учёта"
        verbose_name_plural = "Приборы учёта"
        unique_together = ("account", "service", "serial_number")
        ordering = ("account", "service")

    def __str__(self):
        return f"{self.service} №{self.serial_number} (ЛС {self.account.number})"

    @property
    def last_reading(self):
        return self.readings.order_by("-period").first()


class MeterReading(models.Model):
    """Показание прибора учёта за расчётный период (месяц)."""

    meter = models.ForeignKey(
        Meter, on_delete=models.CASCADE, related_name="readings", verbose_name="Прибор учёта"
    )
    period = models.DateField("Период (первое число месяца)")
    value = models.DecimalField(
        "Показание", max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0"))]
    )
    submitted_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True, blank=True,
        verbose_name="Кем внесено",
    )
    is_manual = models.BooleanField("Внесено вручную нанимателем", default=False)
    created_at = models.DateTimeField("Внесено", auto_now_add=True)

    class Meta:
        verbose_name = "Показание прибора учёта"
        verbose_name_plural = "Показания приборов учёта"
        unique_together = ("meter", "period")
        ordering = ("meter", "-period")
        indexes = [models.Index(fields=["meter", "period"])]

    def __str__(self):
        return f"{self.meter}: {self.value} на {self.period}"

    @property
    def consumption(self) -> Decimal:
        """Потребление за период = текущее показание - предыдущее."""
        previous = (
            MeterReading.objects.filter(meter=self.meter, period__lt=self.period)
            .order_by("-period")
            .first()
        )
        base = previous.value if previous else Decimal("0")
        return self.value - base
