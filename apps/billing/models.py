from decimal import Decimal

from django.db import models

from apps.accounts.models import PersonalAccount
from apps.services.models import Service, Tariff


class ChargeStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    FINAL = "final", "Проведено"


class Charge(models.Model):
    """Начисление по лицевому счёту за расчётный период (месяц).

    Формируется автоматически (см. management-команду generate_monthly_charges
    и apps.billing.tasks) на BILLING_GENERATION_DAY число месяца, но может быть
    скорректировано вручную бухгалтером до перевода в статус "Проведено".
    """

    account = models.ForeignKey(
        PersonalAccount, on_delete=models.PROTECT, related_name="charges", verbose_name="Лицевой счёт"
    )
    period = models.DateField("Расчётный период (первое число месяца)")
    status = models.CharField(
        "Статус", max_length=10, choices=ChargeStatus.choices, default=ChargeStatus.DRAFT
    )

    opening_balance = models.DecimalField(
        "Входящее сальдо", max_digits=12, decimal_places=2, default=Decimal("0")
    )
    accrued_total = models.DecimalField(
        "Начислено", max_digits=12, decimal_places=2, default=Decimal("0")
    )
    paid_total = models.DecimalField(
        "Оплачено", max_digits=12, decimal_places=2, default=Decimal("0")
    )
    closing_balance = models.DecimalField(
        "Исходящее сальдо", max_digits=12, decimal_places=2, default=Decimal("0")
    )

    generated_at = models.DateTimeField("Сформировано", auto_now_add=True)
    generated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True, blank=True,
        verbose_name="Сформировано пользователем", help_text="Пусто — сформировано автоматически",
    )

    class Meta:
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"
        unique_together = ("account", "period")
        ordering = ("-period", "account")
        indexes = [models.Index(fields=["account", "period"]), models.Index(fields=["period"])]

    def __str__(self):
        return f"Начисление ЛС №{self.account.number} за {self.period:%m.%Y}"

    def recalculate_totals(self, save=True):
        self.accrued_total = self.lines.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")
        self.closing_balance = self.opening_balance + self.accrued_total - self.paid_total
        if save:
            self.save(update_fields=["accrued_total", "paid_total", "closing_balance"])


class ChargeLine(models.Model):
    """Строка начисления по одной услуге в рамках Charge."""

    charge = models.ForeignKey(
        Charge, on_delete=models.CASCADE, related_name="lines", verbose_name="Начисление"
    )
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="charge_lines", verbose_name="Услуга"
    )
    tariff = models.ForeignKey(
        Tariff, on_delete=models.PROTECT, related_name="charge_lines", verbose_name="Тариф",
        null=True, blank=True,
    )
    rate = models.DecimalField(
        "Ставка на момент начисления", max_digits=12, decimal_places=4,
        help_text="Снимок ставки тарифа — не меняется при последующем изменении тарифа",
    )
    volume = models.DecimalField(
        "Объём (площадь/чел/потребление)", max_digits=12, decimal_places=3, default=Decimal("1"),
    )
    amount = models.DecimalField("Сумма", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Строка начисления"
        verbose_name_plural = "Строки начислений"
        unique_together = ("charge", "service")
        ordering = ("service__sort_order",)

    def __str__(self):
        return f"{self.service}: {self.amount} ({self.charge})"


class Payment(models.Model):
    """Оплата, поступившая по лицевому счёту (вручную или из банк-выписки)."""

    account = models.ForeignKey(
        PersonalAccount, on_delete=models.CASCADE, related_name="payments", verbose_name="Лицевой счёт"
    )
    charge = models.ForeignKey(
        Charge, on_delete=models.SET_NULL, related_name="payments", null=True, blank=True,
        verbose_name="Отнесено на начисление",
    )
    date = models.DateField("Дата оплаты")
    amount = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    reference = models.CharField("Номер платежа/квитанции", max_length=100, blank=True)

    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True, blank=True,
        verbose_name="Кем внесено",
    )
    created_at = models.DateTimeField("Внесён", auto_now_add=True)

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"
        ordering = ("-date",)
        indexes = [models.Index(fields=["account", "date"])]

    def __str__(self):
        return f"Оплата {self.amount} по ЛС №{self.account.number} от {self.date}"
