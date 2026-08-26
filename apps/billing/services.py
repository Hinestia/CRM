"""Логика формирования ежемесячных начислений.

Вызывается из management-команды generate_monthly_charges и из
Celery-задачи apps.billing.tasks.generate_monthly_charges_task —
оба пути используют одну и ту же функцию, чтобы поведение не расходилось.
"""

from datetime import date
from decimal import Decimal

from django.db import transaction

from apps.accounts.models import AccountStatus, PersonalAccount
from apps.meters.models import MeterReading
from apps.services.models import CalculationMethod, Service

from .models import Charge, ChargeLine


def _volume_for_service(account: PersonalAccount, service: Service, period: date) -> Decimal:
    method = service.calculation_method
    if method == CalculationMethod.PER_AREA:
        return account.unit.billable_area
    if method == CalculationMethod.PER_PERSON:
        return Decimal(account.registered_count)
    if method == CalculationMethod.FIXED:
        return Decimal("1")
    if method == CalculationMethod.PER_CONSUMPTION:
        reading = MeterReading.objects.filter(
            meter__account=account, meter__service=service, period=period
        ).first()
        return reading.consumption if reading else Decimal("0")
    raise ValueError(f"Неизвестный способ расчёта: {method}")


@transaction.atomic
def generate_charge_for_account(account: PersonalAccount, period: date, services=None, user=None) -> Charge:
    """Формирует (или пересобирает, пока черновик) начисление за period для одного ЛС."""
    charge, _ = Charge.objects.get_or_create(
        account=account, period=period, defaults={"generated_by": user},
    )

    previous_period = date(period.year - 1, 12, 1) if period.month == 1 else date(period.year, period.month - 1, 1)
    previous_charge = Charge.objects.filter(account=account, period=previous_period).first()
    charge.opening_balance = previous_charge.closing_balance if previous_charge else Decimal("0")

    services = services or Service.objects.filter(is_active=True)
    for service in services:
        tariff = service.tariff_for_date(period)
        if tariff is None:
            continue
        volume = _volume_for_service(account, service, period)
        amount = (volume * tariff.rate).quantize(Decimal("0.01"))
        ChargeLine.objects.update_or_create(
            charge=charge, service=service,
            defaults={"tariff": tariff, "rate": tariff.rate, "volume": volume, "amount": amount},
        )

    # Перерасчёты, ещё не привязанные ни к одному начислению, попадают в текущее
    charge.recalculations.filter(applied_in_charge__isnull=True).update(applied_in_charge=charge)
    account.recalculations.filter(applied_in_charge__isnull=True).update(applied_in_charge=charge)

    charge.recalculate_totals(save=False)
    charge.save()
    return charge


def generate_monthly_charges(period: date, user=None) -> list[Charge]:
    """Формирует начисления по всем активным лицевым счетам за period."""
    accounts = PersonalAccount.objects.filter(status=AccountStatus.ACTIVE).select_related("unit")
    return [generate_charge_for_account(account, period, user=user) for account in accounts]
