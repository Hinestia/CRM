"""Реестр должников и расчёт пени."""

from datetime import date
from decimal import Decimal

from django.db.models import OuterRef, Subquery

from apps.accounts.models import PersonalAccount
from apps.billing.models import Charge

from .models import PenaltyAccrual, PenaltySettings


def debtor_accounts_queryset():
    """Лицевые счета с положительным исходящим сальдо по последнему начислению
    (реестр должников)."""
    latest_charge = Charge.objects.filter(account=OuterRef("pk")).order_by("-period")
    return (
        PersonalAccount.objects.annotate(
            last_closing_balance=Subquery(latest_charge.values("closing_balance")[:1])
        )
        .filter(last_closing_balance__gt=0)
        .order_by("-last_closing_balance")
    )


def accrue_penalties(on_date: date | None = None) -> list[PenaltyAccrual]:
    """Начисляет пеню по всем просроченным начислениям на указанную дату."""
    on_date = on_date or date.today()
    settings_obj = PenaltySettings.objects.filter(is_active=True).first()
    if settings_obj is None:
        return []

    created = []
    for account in debtor_accounts_queryset():
        charge = (
            Charge.objects.filter(account=account, closing_balance__gt=0)
            .order_by("-period")
            .first()
        )
        if charge is None:
            continue

        due_date = date(charge.period.year, charge.period.month, 1)
        days_overdue = (on_date - due_date).days - settings_obj.grace_period_days
        if days_overdue <= 0:
            continue

        amount = (charge.closing_balance * settings_obj.rate_per_day * days_overdue).quantize(
            Decimal("0.01")
        )
        accrual, _ = PenaltyAccrual.objects.update_or_create(
            charge=charge, calculation_date=on_date,
            defaults={
                "account": account,
                "days_overdue": days_overdue,
                "debt_amount": charge.closing_balance,
                "amount": amount,
            },
        )
        created.append(accrual)
    return created
