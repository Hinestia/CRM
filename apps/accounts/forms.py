from django import forms

from .models import PersonalAccount


class PersonalAccountForm(forms.ModelForm):
    class Meta:
        model = PersonalAccount
        fields = [
            "number", "unit", "status", "registered_count",
            "opened_at", "closed_at", "notes",
        ]
        widgets = {
            "opened_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "closed_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
