from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import PersonalAccount

from .forms import GeneratePeriodForm, PaymentForm
from .models import Charge
from .services import finalize_charge, generate_monthly_charges


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
@require_POST
def charge_finalize(request, pk):
    charge = get_object_or_404(Charge, pk=pk)
    finalize_charge(charge)
    messages.success(
        request,
        f"Начисление за {charge.period:%m.%Y} по ЛС №{charge.account.number} проведено — "
        f"дальше не пересчитывается автоматически.",
    )
    # redirect() умеет и путь ("/accounts/5/"), и имя маршрута — оба варианта
    # приходят из разных мест (карточка ЛС передаёт путь, список начислений
    # своё имя по умолчанию).
    return redirect(request.POST.get("next") or "billing:charge_list")


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
