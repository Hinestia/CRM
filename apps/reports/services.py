"""Формирование печатных отчётов и ведомостей в PDF.

Как и квитанции (apps.receipts), отчёты рендерятся обычным Django-шаблоном
в HTML и конвертируются в PDF через WeasyPrint. В отличие от квитанций
отчёты не сохраняются в БД — они формируются "на лету" по текущим данным
и отдаются пользователю сразу (Content-Disposition: inline), так что PDF
открывается в браузере для просмотра перед печатью, а «Сохранить как»
доступно средствами самого PDF-просмотрщика браузера.
"""

from datetime import date, datetime
from decimal import Decimal

from django.http import HttpResponse
from django.template.loader import render_to_string


def render_pdf_response(template_name: str, context: dict, filename: str) -> HttpResponse:
    from weasyprint import HTML  # импорт здесь — тяжёлая нативная зависимость

    html_content = render_to_string(template_name, context)
    pdf_bytes = HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


def parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


def build_reconciliation_rows(account, date_from: date, date_to: date):
    """Хронологическая лента начислений и оплат по ЛС за период с бегущим
    сальдо — основа акта сверки."""
    from apps.billing.models import Charge, Payment

    charges = Charge.objects.filter(
        account=account, period__gte=date_from, period__lte=date_to
    ).order_by("period")
    payments = Payment.objects.filter(
        account=account, date__gte=date_from, date__lte=date_to
    ).order_by("date")

    opening_charge = (
        Charge.objects.filter(account=account, period__lt=date_from).order_by("-period").first()
    )
    opening_balance = opening_charge.closing_balance if opening_charge else Decimal("0")

    rows = []
    for charge in charges:
        rows.append({
            "date": charge.period,
            "operation": f"Начисление за {charge.period:%m.%Y}",
            "debit": charge.accrued_total,
            "credit": Decimal("0"),
        })
    for payment in payments:
        label = "Оплата" + (f" №{payment.reference}" if payment.reference else "")
        rows.append({
            "date": payment.date, "operation": label,
            "debit": Decimal("0"), "credit": payment.amount,
        })
    rows.sort(key=lambda r: r["date"])

    balance = opening_balance
    for row in rows:
        balance += row["debit"] - row["credit"]
        row["balance"] = balance

    return rows, opening_balance, balance
