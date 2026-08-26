from decimal import Decimal

from django.db import models


class CalculationMethod(models.TextChoices):
    PER_AREA = "per_area", "руб/м² (площадь)"
    PER_PERSON = "per_person", "руб/чел (зарегистрированные лица)"
    FIXED = "fixed", "фиксированная сумма на лицевой счёт"
    PER_CONSUMPTION = "per_consumption", "руб/куб.м, руб/кВт·ч (по показаниям приборов учёта)"


class Service(models.Model):
    """Справочник услуг ЖКУ. Новые услуги добавляются без изменения кода."""

    code = models.SlugField("Код услуги", max_length=50, unique=True)
    name = models.CharField("Наименование", max_length=150)
    calculation_method = models.CharField(
        "Способ расчёта", max_length=20, choices=CalculationMethod.choices
    )
    unit_of_measure = models.CharField(
        "Единица измерения", max_length=20, blank=True,
        help_text="м², чел., м³, кВт·ч — для отображения в квитанции",
    )
    is_active = models.BooleanField("Активна", default=True)
    sort_order = models.PositiveSmallIntegerField("Порядок в квитанции", default=100)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Справочник услуг"
        ordering = ("sort_order", "name")

    def __str__(self):
        return self.name

    @property
    def requires_meter(self):
        return self.calculation_method == CalculationMethod.PER_CONSUMPTION

    def tariff_for_date(self, on_date):
        """Действующий тариф на указанную дату (для начисления/перерасчёта)."""
        return (
            self.tariffs.filter(valid_from__lte=on_date)
            .filter(models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=on_date))
            .order_by("-valid_from")
            .first()
        )


class Tariff(models.Model):
    """Тариф услуги, действующий в диапазоне дат.

    История тарифов хранится как набор непересекающихся периодов,
    что позволяет корректно пересчитывать начисления за прошлые периоды
    при изменении тарифа задним числом.
    """

    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="tariffs", verbose_name="Услуга"
    )
    rate = models.DecimalField(
        "Ставка", max_digits=12, decimal_places=4,
        help_text="Значение зависит от способа расчёта услуги (руб/м², руб/чел, руб. и т.д.)",
    )
    valid_from = models.DateField("Действует с")
    valid_to = models.DateField("Действует по", null=True, blank=True)

    created_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="+", verbose_name="Кем установлен",
        null=True, blank=True,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ("service", "-valid_from")
        indexes = [models.Index(fields=["service", "valid_from", "valid_to"])]

    def __str__(self):
        period = f"с {self.valid_from}" + (f" по {self.valid_to}" if self.valid_to else "")
        return f"{self.service}: {self.rate} ({period})"
