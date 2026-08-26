from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import PersonalAccount

from .forms import MeterForm, MeterReadingForm
from .models import Meter


@login_required
def meter_create(request, account_pk):
    account = get_object_or_404(PersonalAccount, pk=account_pk)
    if request.method == "POST":
        form = MeterForm(request.POST)
        if form.is_valid():
            meter = form.save(commit=False)
            meter.account = account
            meter.save()
            messages.success(request, "Прибор учёта добавлен.")
            return redirect("accounts:detail", pk=account.pk)
    else:
        form = MeterForm()
    return render(request, "meters/meter_form.html", {"form": form, "account": account})


@login_required
def reading_create(request, meter_pk):
    meter = get_object_or_404(Meter.objects.select_related("account", "service"), pk=meter_pk)
    if request.method == "POST":
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.meter = meter
            reading.submitted_by = request.user
            reading.save()
            messages.success(request, "Показание внесено.")
            return redirect("accounts:detail", pk=meter.account_id)
    else:
        form = MeterReadingForm()
    return render(request, "meters/reading_form.html", {"form": form, "meter": meter})
