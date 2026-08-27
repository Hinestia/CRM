"""Логика формирования ежемесячных начислений.

Три входные точки, все опираются на одну и ту же generate_charge_for_account,
чтобы поведение не расходилось:
  - generate_monthly_charges(period) — явный запрос за конкретный период
    (форма «Сформировать начисления за период», management-команда).
  - catch_up_charges() — самовосстанавливающийся автозапуск из Celery Beat
    (см. apps.billing.tasks): каждый день доначисляет всё, чего не хватает,
    по каждому активному ЛС, включая пропущенные месяцы после простоя.
  - management-команда generate_monthly_charges (см. management/commands/).
"""

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from apps.accounts.models import AccountStatus, PersonalAccount
from apps.meters.models import MeterReading
from apps.services.models import CalculationMethod, Service

from .models import Charge, ChargeLine, ChargeStatus


def _shift_period(period: date, months: int) -> date:
    """Сдвигает расчётный период (всегда 1-е число месяца) на months
    месяцев — может быть отрицательным."""
    total = period.year * 12 + (period.month - 1) + months
    year, month = divmod(total, 12)
    return date(year, month + 1, 1)


def _volume_for_service(account: PersonalAccount, service: Service, period: date) -> Decimal:
    method = service.calculation_method
    if method == CalculationMethod.PER_AREA:
        return account.unit.area_total
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
    """Формирует (или пересобирает, пока не проведено) начисление за period
    для одного ЛС.

    Если начисление за этот период уже «Проведено» — функция его не
    трогает и просто возвращает как есть: смена тарифа задним числом не
    должна затрагивать закрытые периоды. Проверка — здесь, а не только в
    UI, чтобы повторный вызов (вручную, из Celery, из management-команды)
    не мог случайно переписать уже закрытый месяц.
    """
    charge, _ = Charge.objects.get_or_create(
        account=account, period=period, defaults={"generated_by": user},
    )
    if charge.status == ChargeStatus.FINAL:
        return charge

    previous_period = _shift_period(period, -1)
    previous_charge = Charge.objects.filter(account=account, period=previous_period).first()
    charge.opening_balance = previous_charge.closing_balance if previous_charge else Decimal("0")

    services = services if services is not None else account.services.filter(is_active=True)
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

    charge.recalculate_totals(save=False)
    charge.save()

    # Начисление за текущий период сформировано — значит, предыдущий месяц
    # точно завершён, его можно закрыть автоматически (если ещё не закрыт
    # вручную раньше). Дальнейшие изменения тарифов его больше не затронут.
    if previous_charge and previous_charge.status == ChargeStatus.DRAFT:
        previous_charge.status = ChargeStatus.FINAL
        previous_charge.save(update_fields=["status"])

    return charge


def finalize_charge(charge: Charge) -> Charge:
    """Ручное закрытие периода («Провести») — можно раньше, чем
    сформируется следующий период; после этого начисление больше не
    пересчитывается автоматически."""
    if charge.status != ChargeStatus.FINAL:
        charge.status = ChargeStatus.FINAL
        charge.save(update_fields=["status"])
    return charge


def generate_monthly_charges(period: date, user=None) -> list[Charge]:
    """Формирует начисления по всем активным лицевым счетам строго за
    указанный period — явный ручной запуск (форма/management-команда).
    Для регулярного автозапуска см. catch_up_charges."""
    accounts = PersonalAccount.objects.filter(status=AccountStatus.ACTIVE).select_related("unit")
    return [generate_charge_for_account(account, period, user=user) for account in accounts]


def catch_up_charges(user=None) -> list[Charge]:
    """Идемпотентная функция для ежедневного вызова из Celery Beat.

    Донасчитывает по каждому активному ЛС все периоды, которых не хватает,
    вплоть до текущего (если уже наступило число автогенерации —
    settings.BILLING_GENERATION_DAY). Безопасна к повторному запуску и к
    простою Celery/сервера любой длины: при восстановлении просто
    досчитывает всё недостающее по порядку (opening_balance каждого периода
    берётся из закрытия предыдущего, поэтому важен именно хронологический
    порядок, а не «пропустить и начать с текущего месяца»).
    """
    today = date.today()
    current_period = date(today.year, today.month, 1)
    target_period = (
        current_period if today.day >= settings.BILLING_GENERATION_DAY
        else _shift_period(current_period, -1)
    )

    generated = []
    accounts = PersonalAccount.objects.filter(status=AccountStatus.ACTIVE).select_related("unit")
    for account in accounts:
        last_charge = account.charges.order_by("-period").first()
        if last_charge:
            period = _shift_period(last_charge.period, 1)
        else:
            period = date(account.opened_at.year, account.opened_at.month, 1)
        while period <= target_period:
            generated.append(generate_charge_for_account(account, period, user=user))
            period = _shift_period(period, 1)
    return generated
