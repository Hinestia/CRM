from decimal import Decimal

from django import forms

from .models import House, Street, Unit, UnitType


class StreetForm(forms.ModelForm):
    class Meta:
        model = Street
        fields = ["type", "name"]


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ["street", "number", "building"]


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        # area_total не редактируется — считается автоматически как
        # area_living + area_non_living (см. Unit.save()). Площадь
        # балкона в расчёт не входит (см. ТЗ) — отдельного поля для неё нет.
        fields = ["number", "type", "area_living", "area_non_living"]


class UnitWithHouseForm(forms.Form):
    """Форма для модалки «Новое помещение» на карточке лицевого счёта:
    заводит (или переиспользует) дом на выбранной улице и сразу создаёт
    в нём помещение — одной формой, без перехода в раздел «Адресный фонд»."""

    street = forms.ModelChoiceField(queryset=Street.objects.all(), label="Улица")
    house_number = forms.CharField(label="Номер дома", max_length=10)
    building = forms.CharField(label="Литера/строение", max_length=10, required=False)
    unit_number = forms.CharField(label="Номер квартиры/помещения", max_length=10)
    unit_type = forms.ChoiceField(
        label="Тип помещения", choices=UnitType.choices, initial=UnitType.RESIDENTIAL
    )
    area_living = forms.DecimalField(
        label="S жилая, м²", max_digits=8, decimal_places=2,
        min_value=Decimal("0"), initial=Decimal("0"),
    )
    area_non_living = forms.DecimalField(
        label="S нежилая, м²", max_digits=8, decimal_places=2,
        min_value=Decimal("0"), initial=Decimal("0"),
    )
