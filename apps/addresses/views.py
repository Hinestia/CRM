from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import HouseForm, StreetForm, UnitForm, UnitWithHouseForm
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
def street_quick_create(request):
    """Модалка «Новая улица», открытая из модалки «Новое помещение» на
    карточке ЛС. Возвращает пользователя обратно в модалку помещения —
    с только что созданной улицей предвыбранной."""
    if request.method == "POST":
        form = StreetForm(request.POST)
        if form.is_valid():
            street = form.save()
            messages.success(request, f"Улица «{street}» добавлена.")
            unit_form = UnitWithHouseForm(initial={"street": street.pk})
            return render(request, "addresses/_unit_quick_create_modal.html", {"form": unit_form})
    else:
        form = StreetForm()
    return render(request, "addresses/_street_quick_create_modal.html", {"form": form})


@login_required
def unit_quick_create(request):
    """Модалка «Новое помещение» на карточке лицевого счёта: заводит дом
    (если такого ещё нет) и помещение в нём, затем через out-of-band swap
    подставляет новое помещение в выпадающий список на форме ЛС."""
    if request.method == "POST":
        form = UnitWithHouseForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            house, _ = House.objects.get_or_create(
                street=cd["street"], number=cd["house_number"], building=cd["building"],
            )
            if Unit.objects.filter(house=house, number=cd["unit_number"]).exists():
                form.add_error("unit_number", "Такое помещение уже есть в этом доме.")
            else:
                unit = Unit.objects.create(
                    house=house, number=cd["unit_number"], type=cd["unit_type"],
                    area_living=cd["area_living"], area_non_living=cd["area_non_living"],
                )
                messages.success(request, f"Помещение «{unit}» добавлено.")
                return render(request, "addresses/_unit_oob_swap.html", {
                    "units": Unit.objects.select_related("house__street"),
                    "selected_unit": unit,
                })
    else:
        form = UnitWithHouseForm()
    return render(request, "addresses/_unit_quick_create_modal.html", {"form": form})


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
