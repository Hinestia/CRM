from datetime import date, timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Contract


@shared_task
def notify_contract_expiry_task():
    """Ежедневно проверяет договоры, до окончания которых остался
    CONTRACT_EXPIRY_WARNING_DAYS дней, и уведомляет ответственных
    сотрудников по email (и оставляет отметку, чтобы не дублировать)."""
    threshold = date.today() + timedelta(days=settings.CONTRACT_EXPIRY_WARNING_DAYS)
    contracts = Contract.objects.filter(
        end_date=threshold, expiry_notified_at__isnull=True
    ).prefetch_related("responsible_employees")

    notified = 0
    for contract in contracts:
        emails = [u.email for u in contract.responsible_employees.all() if u.email]
        if emails:
            send_mail(
                subject=f"Договор №{contract.number} истекает {contract.end_date:%d.%m.%Y}",
                message=(
                    f"Договор №{contract.number} по ЛС №{contract.account.number} "
                    f"истекает {contract.end_date:%d.%m.%Y}. Требуется продление или закрытие."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
            )
        contract.expiry_notified_at = timezone.now()
        contract.save(update_fields=["expiry_notified_at"])
        notified += 1
    return f"Уведомлено договоров: {notified}"
