from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.billing.models import Charge

from .models import Receipt
from .services import generate_receipt_pdf, generate_receipts_for_period


@login_required
def receipt_list(request):
    receipts = Receipt.objects.select_related("charge__account").order_by("-generated_at")[:100]
    return render(request, "receipts/list.html", {"receipts": receipts})


@login_required
def generate_for_period(request):
    if request.method == "POST":
        raw_period = request.POST.get("period")
        year, month = (int(p) for p in raw_period.split("-")[:2])
        period = date(year, month, 1)
        result = generate_receipts_for_period(period, user=request.user)
        messages.success(request, f"Сформировано квитанций: {len(result)} за {period:%m.%Y}.")
    return redirect("receipts:list")


@login_required
@require_POST
def generate_for_charge(request, charge_pk):
    charge = get_object_or_404(Charge, pk=charge_pk)
    generate_receipt_pdf(charge, user=request.user)
    messages.success(request, f"Квитанция за {charge.period:%m.%Y} сформирована.")
    return redirect("accounts:detail", pk=charge.account_id)
