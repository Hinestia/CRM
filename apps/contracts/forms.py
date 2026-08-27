from django import forms

from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["account", "number", "signed_date", "end_date", "responsible_employees"]
        widgets = {
            "signed_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "responsible_employees": forms.CheckboxSelectMultiple,
        }


class ContractQuickForm(forms.ModelForm):
    """Та же форма без выбора ЛС — для модалки, открытой с карточки
    конкретного лицевого счёта (account подставляется во view)."""

    class Meta:
        model = Contract
        fields = ["number", "signed_date", "end_date", "responsible_employees"]
        widgets = {
            "signed_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "responsible_employees": forms.CheckboxSelectMultiple,
        }
