from datetime import date

from celery import shared_task
from django.core.mail import EmailMessage

from .models import Receipt
from .services import generate_receipts_for_period


@shared_task
def generate_receipts_task(year: int, month: int):
    period = date(year, month, 1)
    receipts = generate_receipts_for_period(period)
    return f"Сформировано {len(receipts)} квитанций за {period:%m.%Y}"


@shared_task
def email_receipt_task(receipt_id: int):
    receipt = Receipt.objects.select_related("charge__account").get(pk=receipt_id)
    tenant = receipt.charge.account.current_responsible
    if not tenant or not tenant.email:
        return f"У ЛС №{receipt.charge.account.number} не указан email нанимателя"

    message = EmailMessage(
        subject=f"Квитанция за {receipt.charge.period:%m.%Y} — ЛС №{receipt.charge.account.number}",
        body="Квитанция на оплату ЖКУ во вложении.",
        to=[tenant.email],
    )
    message.attach_file(receipt.file.path)
    message.send()

    from django.utils import timezone
    receipt.emailed_at = timezone.now()
    receipt.save(update_fields=["emailed_at"])
    return f"Квитанция отправлена на {tenant.email}"


@shared_task
def email_receipts_for_period_task(year: int, month: int):
    period = date(year, month, 1)
    receipt_ids = Receipt.objects.filter(charge__period=period).values_list("id", flat=True)
    for receipt_id in receipt_ids:
        email_receipt_task.delay(receipt_id)
    return f"Поставлено в очередь на отправку: {len(receipt_ids)}"
