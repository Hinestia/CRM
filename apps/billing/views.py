from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import PersonalAccount

from .forms import GeneratePeriodForm, PaymentForm, RecalculationForm
from .models import Charge
from .services import generate_monthly_charges


@login_required
def charge_list(request):
    period = request.GET.get("period", "")
    charges = Charge.objects.select_related("account").order_by("-period", "account__number")
    if period:
        year, month = (int(p) for p in period.split("-")[:2])
        charges = charges.filter(period__year=year, period__month=month)
    charges = charges[:200]

    generate_form = GeneratePeriodForm()
    if request.method == "POST":
        generate_form = GeneratePeriodForm(request.POST)
        if generate_form.is_valid():
            result = generate_monthly_charges(generate_form.cleaned_data["period"], user=request.user)
            messages.success(request, f"Сформировано начислений: {len(result)}.")
            return redirect("billing:charge_list")

    return render(request, "billing/charge_list.html", {
        "charges": charges, "period": period, "generate_form": generate_form,
    })


@login_required
def recalculation_create(request, account_pk):
    account = get_object_or_404(PersonalAccount, pk=account_pk)
    if request.method == "POST":
        form = RecalculationForm(request.POST)
        if form.is_valid():
            recalc = form.save(commit=False)
            recalc.account = account
            recalc.created_by = request.user
            recalc.save()
            messages.success(request, "Перерасчёт сохранён.")
            return redirect("accounts:detail", pk=account.pk)
    else:
        form = RecalculationForm()
    return render(request, "billing/recalculation_form.html", {"form": form, "account": account})


@login_required
def payment_create(request, account_pk):
    account = get_object_or_404(PersonalAccount, pk=account_pk)
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.account = account
            payment.created_by = request.user

            # Относим оплату на самое свежее начисление по счёту и пересчитываем его сальдо
            latest_charge = account.charges.order_by("-period").first()
            if latest_charge:
                payment.charge = latest_charge

            payment.save()

            if latest_charge:
                latest_charge.paid_total += payment.amount
                latest_charge.recalculate_totals()

            messages.success(request, "Оплата сохранена.")
            return redirect("accounts:detail", pk=account.pk)
    else:
        form = PaymentForm()
    return render(request, "billing/payment_form.html", {"form": form, "account": account})
