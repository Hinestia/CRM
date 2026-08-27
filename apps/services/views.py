from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ServiceForm, TariffForm
from .models import Service


@login_required
def service_list(request):
    services = Service.objects.order_by("sort_order", "name")
    today = date.today()
    rows = [(service, service.tariff_for_date(today)) for service in services]
    return render(request, "services/list.html", {"rows": rows})


@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    tariffs = service.tariffs.order_by("-valid_from")
    return render(request, "services/detail.html", {"service": service, "tariffs": tariffs})


@login_required
def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"Услуга «{service.name}» добавлена.")
            return redirect("services:detail", pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, "services/form.html", {"form": form, "title": "Новая услуга"})


@login_required
def tariff_create(request, service_pk):
    service = get_object_or_404(Service, pk=service_pk)
    if request.method == "POST":
        form = TariffForm(request.POST)
        if form.is_valid():
            tariff = form.save(commit=False)
            tariff.service = service
            tariff.created_by = request.user

            open_tariff = service.tariffs.filter(valid_to__isnull=True).exclude(pk=tariff.pk).first()
            if open_tariff and open_tariff.valid_from < tariff.valid_from:
                open_tariff.valid_to = tariff.valid_from - timedelta(days=1)
                open_tariff.save(update_fields=["valid_to"])

            tariff.save()
            messages.success(request, f"Новый тариф для «{service.name}» сохранён.")
            return redirect("services:detail", pk=service.pk)
    else:
        form = TariffForm(initial={"valid_from": date.today()})
    return render(request, "services/tariff_form.html", {"form": form, "service": service})
