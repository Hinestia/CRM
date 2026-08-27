from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render

from apps.billing.models import Charge
from apps.billing.services import generate_charge_for_account

from .forms import PersonalAccountForm
from .models import PersonalAccount


def _annotated_accounts():
    latest_charge = Charge.objects.filter(account=OuterRef("pk")).order_by("-period")
    return PersonalAccount.objects.select_related("unit__house__street").annotate(
        last_closing_balance=Subquery(latest_charge.values("closing_balance")[:1])
    )


@login_required
def account_list(request):
    q = request.GET.get("q", "").strip()
    debt_filter = request.GET.get("debt", "")

    accounts = _annotated_accounts()
    if q:
        accounts = accounts.filter(
            Q(number__icontains=q)
            | Q(unit__house__street__name__icontains=q)
            | Q(unit__house__number__icontains=q)
            | Q(unit__number__icontains=q)
            | Q(tenant_assignments__tenant__last_name__icontains=q)
            | Q(tenant_assignments__tenant__first_name__icontains=q)
            | Q(tenant_assignments__tenant__middle_name__icontains=q)
        ).distinct()
    if debt_filter == "debt":
        accounts = accounts.filter(last_closing_balance__gt=0)
    elif debt_filter == "no_debt":
        accounts = accounts.filter(Q(last_closing_balance__lte=0) | Q(last_closing_balance__isnull=True))

    accounts = accounts.order_by("number")
    paginator = Paginator(accounts, 30)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "accounts/list.html", {
        "page": page, "q": q, "debt_filter": debt_filter,
    })


@login_required
def account_detail(request, pk):
    account = get_object_or_404(
        PersonalAccount.objects.select_related("unit__house__street").prefetch_related("services"),
        pk=pk,
    )
    tenant_assignments = account.tenant_assignments.select_related("tenant").order_by("-start_date")
    charges = account.charges.order_by("-period")
    contracts = account.contracts.select_related("generated_file").order_by("-signed_date")
    payments = account.payments.order_by("-date")[:20]
    penalty_accruals = account.penalty_accruals.order_by("-calculation_date")[:10]

    return render(request, "accounts/detail.html", {
        "account": account,
        "tenant_assignments": tenant_assignments,
        "charges": charges,
        "contracts": contracts,
        "payments": payments,
        "penalty_accruals": penalty_accruals,
    })


@login_required
def account_create(request):
    if request.method == "POST":
        form = PersonalAccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f"Лицевой счёт №{account.number} создан.")
            return redirect("accounts:detail", pk=account.pk)
    else:
        form = PersonalAccountForm(initial={"opened_at": date.today()})
    return render(request, "accounts/form.html", {"form": form, "title": "Новый лицевой счёт"})


@login_required
def account_update(request, pk):
    account = get_object_or_404(PersonalAccount, pk=pk)
    if request.method == "POST":
        form = PersonalAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Лицевой счёт обновлён.")
            return redirect("accounts:detail", pk=account.pk)
    else:
        form = PersonalAccountForm(instance=account)
    return render(request, "accounts/form.html", {
        "form": form, "title": f"Редактирование ЛС №{account.number}", "account": account,
    })


@login_required
def account_generate_charge(request, pk):
    account = get_object_or_404(PersonalAccount, pk=pk)
    if request.method == "POST":
        raw_period = request.POST.get("period")
        year, month = (int(p) for p in raw_period.split("-")[:2])
        period = date(year, month, 1)
        generate_charge_for_account(account, period, user=request.user)
        messages.success(request, f"Начисление за {period:%m.%Y} сформировано.")
    return redirect("accounts:detail", pk=account.pk)
