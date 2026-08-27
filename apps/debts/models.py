from decimal import Decimal

from django.db import models

from apps.accounts.models import PersonalAccount
from apps.billing.models import Charge


class PenaltySettings(models.Model):
    """Настройки расчёта пени (единые на систему).

    Простая модель с одной действующей записью (is_active=True).
    По умолчанию соответствует ч.14 ст.155 ЖК РФ: пеня не начисляется
    в течение grace_period_days дней просрочки, далее — rate_per_day
    от суммы долга за каждый день (1/300 ключевой ставки ЦБ РФ).
    Более сложная многоступенчатая формула (1/130 после 91 дня) может быть
    добавлена позже без изменения остальной схемы.
    """

    name = models.CharField("Название", max_length=100, default="Основные настройки пени")
    grace_period_days = models.PositiveSmallIntegerField("Льготный период, дней", default=30)
    rate_per_day = models.DecimalField(
        "Ставка пени в день", max_digits=8, decimal_places=6, default=Decimal("0.0003"),
        help_text="Доля от суммы долга, начисляемая за каждый день просрочки (например 1/300 ставки ЦБ)",
    )
    is_active = models.BooleanField("Действующие настройки", default=True)

    class Meta:
        verbose_name = "Настройки пени"
        verbose_name_plural = "Настройки пени"

    def __str__(self):
        return self.name


class PenaltyAccrual(models.Model):
    """Начисленная пеня по лицевому счёту за конкретное просроченное начисление."""

    account = models.ForeignKey(
        PersonalAccount, on_delete=models.CASCADE, related_name="penalty_accruals",
        verbose_name="Лицевой счёт",
    )
    charge = models.ForeignKey(
        Charge, on_delete=models.CASCADE, related_name="penalty_accruals", verbose_name="Начисление"
    )
    calculation_date = models.DateField("Дата расчёта пени")
    days_overdue = models.PositiveIntegerField("Дней просрочки")
    debt_amount = models.DecimalField("Сумма долга на дату расчёта", max_digits=12, decimal_places=2)
    amount = models.DecimalField("Сумма пени", max_digits=12, decimal_places=2)

    created_at = models.DateTimeField("Рассчитано", auto_now_add=True)

    class Meta:
        verbose_name = "Начисление пени"
        verbose_name_plural = "Начисления пени"
        unique_together = ("charge", "calculation_date")
        ordering = ("-calculation_date",)

    def __str__(self):
        return f"Пеня {self.amount} по ЛС №{self.account.number} на {self.calculation_date}"


