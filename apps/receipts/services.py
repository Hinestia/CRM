"""Генерация PDF-квитанций.

Используется WeasyPrint: рендерим обычный Django-шаблон в HTML и
конвертируем в PDF — не нужно верстать координаты вручную (в отличие от
ReportLab), поддерживается кириллица и CSS, шаблон правится дизайнером
без знания Python.
"""

from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from .models import Receipt


def generate_receipt_pdf(charge, user=None) -> Receipt:
    from weasyprint import HTML  # импорт здесь — тяжёлая нативная зависимость

    responsible = charge.account.current_responsible
    html_content = render_to_string(
        "receipts/receipt.html", {"charge": charge, "responsible": responsible}
    )
    pdf_bytes = HTML(string=html_content).write_pdf()

    receipt, _ = Receipt.objects.update_or_create(
        charge=charge, defaults={"generated_by": user},
    )
    filename = f"{charge.account.number}_{charge.period:%Y-%m}.pdf"
    receipt.file.save(filename, ContentFile(pdf_bytes), save=True)
    return receipt


def generate_receipts_for_period(period, user=None) -> list[Receipt]:
    from apps.billing.models import Charge

    receipts = []
    for charge in Charge.objects.filter(period=period).select_related("account"):
        receipts.append(generate_receipt_pdf(charge, user=user))
    return receipts
