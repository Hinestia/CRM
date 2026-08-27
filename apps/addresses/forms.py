from django import forms

from .models import House, Street, Unit


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
        # area_living + area_non_living + area_balcony (см. Unit.save()).
        fields = [
            "number", "type", "area_living", "area_non_living",
            "area_balcony", "balcony_coefficient",
        ]
