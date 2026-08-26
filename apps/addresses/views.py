from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import HouseForm, StreetForm, UnitForm
from .models import House, Unit


@login_required
def house_list(request):
    q = request.GET.get("q", "").strip()
    houses = House.objects.select_related("street").order_by("street__name", "number")
    if q:
        houses = houses.filter(
            Q(street__name__icontains=q) | Q(number__icontains=q) | Q(building__icontains=q)
        )
    return render(request, "addresses/house_list.html", {"houses": houses, "q": q})


@login_required
def house_detail(request, pk):
    house = get_object_or_404(House.objects.select_related("street"), pk=pk)
    units = house.units.order_by("number").prefetch_related("accounts")
    return render(request, "addresses/house_detail.html", {"house": house, "units": units})


@login_required
def house_create(request):
    if request.method == "POST":
        form = HouseForm(request.POST)
        if form.is_valid():
            house = form.save()
            messages.success(request, "Дом добавлен.")
            return redirect("addresses:house_detail", pk=house.pk)
    else:
        form = HouseForm()
    return render(request, "addresses/house_form.html", {"form": form, "title": "Новый дом"})


@login_required
def street_create(request):
    if request.method == "POST":
        form = StreetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Улица добавлена.")
            return redirect("addresses:house_create")
    else:
        form = StreetForm()
    return render(request, "addresses/house_form.html", {"form": form, "title": "Новая улица"})


@login_required
def unit_create(request, house_pk):
    house = get_object_or_404(House, pk=house_pk)
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.house = house
            unit.save()
            messages.success(request, "Помещение добавлено.")
            return redirect("addresses:house_detail", pk=house.pk)
    else:
        form = UnitForm()
    return render(request, "addresses/unit_form.html", {
        "form": form, "title": f"Новое помещение — {house}", "house": house,
    })


@login_required
def unit_update(request, pk):
    unit = get_object_or_404(Unit.objects.select_related("house"), pk=pk)
    if request.method == "POST":
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, "Характеристики помещения обновлены.")
            return redirect("addresses:house_detail", pk=unit.house_id)
    else:
        form = UnitForm(instance=unit)
    return render(request, "addresses/unit_form.html", {
        "form": form, "title": f"Помещение {unit.number} — {unit.house}", "house": unit.house,
    })
