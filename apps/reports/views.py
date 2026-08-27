from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import PersonalAccount
from apps.billing.models import Charge
from apps.debts.services import debtor_accounts_queryset

from .services import build_reconciliation_rows, parse_date, render_pdf_response


@login_required
def reports_index(request):
    accounts = PersonalAccount.objects.order_by("number")
    return render(request, "reports/index.html", {"accounts": accounts})


@login_required
def accounts_register_pdf(request):
    latest_charge = Charge.objects.filter(account=OuterRef("pk")).order_by("-period")
    accounts = (
        PersonalAccount.objects.select_related("unit__house__street")
        .prefetch_related("services")
        .annotate(last_closing_balance=Subquery(latest_charge.values("closing_balance")[:1]))
        .order_by("number")
    )
    return render_pdf_response(
        "reports/accounts_register.html",
        {"accounts": accounts, "today": date.today()},
        "reestr_licevyh_schetov.pdf",
    )


@login_required
def accruals_statement_pdf(request):
    raw_period = request.GET.get("period")
    if not raw_period:
        messages.error(request, "Укажите период для ведомости начислений.")
        return redirect("reports:index")
    year, month = (int(p) for p in raw_period.split("-")[:2])
    period = date(year, month, 1)

    charges = (
        Charge.objects.filter(period=period)
        .select_related("account__unit__house__street")
        .order_by("account__number")
    )
    totals = charges.aggregate(
        opening=models.Sum("opening_balance"),
        accrued=models.Sum("accrued_total"),
        paid=models.Sum("paid_total"),
        closing=models.Sum("closing_balance"),
    )
    return render_pdf_response(
        "reports/accruals_statement.html",
        {"charges": charges, "period": period, "totals": totals},
        f"vedomost_nachisleniy_{period:%Y-%m}.pdf",
    )


@login_required
def debtors_register_pdf(request):
    accounts = debtor_accounts_queryset().select_related("unit__house__street")
    return render_pdf_response(
        "reports/debtors_register.html",
        {"accounts": accounts, "today": date.today()},
        "reestr_dolzhnikov.pdf",
    )


@login_required
def reconciliation_act_pdf(request):
    account_id = request.GET.get("account")
    if not account_id:
        messages.error(request, "Выберите лицевой счёт для акта сверки.")
        return redirect("reports:index")
    account = get_object_or_404(
        PersonalAccount.objects.select_related("unit__house__street"), pk=account_id
    )
    date_from = parse_date(request.GET.get("date_from")) or account.opened_at
    date_to = parse_date(request.GET.get("date_to")) or date.today()

    rows, opening_balance, closing_balance = build_reconciliation_rows(account, date_from, date_to)
    return render_pdf_response(
        "reports/reconciliation_act.html",
        {
            "account": account, "date_from": date_from, "date_to": date_to,
            "rows": rows, "opening_balance": opening_balance, "closing_balance": closing_balance,
            "responsible": account.current_responsible,
        },
        f"akt_sverki_{account.number}.pdf",
    )
