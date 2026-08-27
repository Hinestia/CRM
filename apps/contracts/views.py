from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.urls import reverse

from apps.accounts.models import PersonalAccount
from config.htmx_utils import htmx_redirect

from .forms import ContractForm, ContractQuickForm
from .models import Contract
from .services import NoActiveContractTemplate, generate_contract_pdf


@login_required
def contract_list(request):
    q = request.GET.get("q", "").strip()
    expiring_only = request.GET.get("expiring") == "1"

    contracts = Contract.objects.select_related("account").order_by("-signed_date")
    if q:
        contracts = contracts.filter(Q(number__icontains=q) | Q(account__number__icontains=q))
    if expiring_only:
        contracts = contracts.filter(
            end_date__isnull=False,
            end_date__gte=date.today(),
            end_date__lte=date.today() + timedelta(days=30),
        )
    return render(request, "contracts/list.html", {
        "contracts": contracts, "q": q, "expiring_only": expiring_only,
    })


@login_required
def contract_create(request):
    account_id = request.GET.get("account") or request.POST.get("account")
    if request.method == "POST":
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            messages.success(request, f"Договор №{contract.number} добавлен.")
            return redirect("accounts:detail", pk=contract.account_id)
    else:
        initial = {}
        if account_id:
            initial["account"] = account_id
        form = ContractForm(initial=initial)
    account = PersonalAccount.objects.filter(pk=account_id).first() if account_id else None
    return render(request, "contracts/form.html", {
        "form": form, "title": "Новый договор", "account": account,
    })


@login_required
def contract_create_for_account(request, account_pk):
    """Добавить договор прямо с карточки лицевого счёта — модальным окном,
    без выбора ЛС (он уже известен из URL)."""
    account = get_object_or_404(PersonalAccount, pk=account_pk)
    if request.method == "POST":
        form = ContractQuickForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.account = account
            contract.save()
            form.save_m2m()
            messages.success(request, f"Договор №{contract.number} добавлен.")
            return htmx_redirect(reverse("accounts:detail", args=[account.pk]))
    else:
        form = ContractQuickForm()
    return render(request, "contracts/_contract_modal.html", {
        "form": form, "account": account, "title": "Новый договор",
        "post_url": reverse("contracts:create_for_account", args=[account.pk]),
    })


@login_required
def contract_update(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        form = ContractQuickForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, "Договор обновлён.")
            return htmx_redirect(reverse("accounts:detail", args=[contract.account_id]))
    else:
        form = ContractQuickForm(instance=contract)
    return render(request, "contracts/_contract_modal.html", {
        "form": form, "account": contract.account, "title": f"Договор №{contract.number}",
        "post_url": reverse("contracts:update", args=[contract.pk]),
    })


@login_required
@require_POST
def contract_generate_pdf(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    try:
        generate_contract_pdf(contract, user=request.user)
        messages.success(request, f"Печатная форма договора №{contract.number} сформирована.")
    except NoActiveContractTemplate:
        messages.error(
            request,
            "Нет активного шаблона договора — загрузите его в админке "
            "(Договоры → Шаблоны договора).",
        )
    except RuntimeError as exc:
        messages.error(request, str(exc))
    return redirect("accounts:detail", pk=contract.account_id)
