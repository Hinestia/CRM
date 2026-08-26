from django import forms

from .models import Service, Tariff


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["code", "name", "calculation_method", "unit_of_measure", "is_active", "sort_order"]


class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ["rate", "valid_from"]
        widgets = {
            "valid_from": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
