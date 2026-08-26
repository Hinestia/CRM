from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import PersonalAccount

from .forms import ContractForm
from .models import Contract


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
def contract_update(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, "Договор обновлён.")
            return redirect("accounts:detail", pk=contract.account_id)
    else:
        form = ContractForm(instance=contract)
    return render(request, "contracts/form.html", {
        "form": form, "title": f"Договор №{contract.number}", "account": contract.account,
    })
