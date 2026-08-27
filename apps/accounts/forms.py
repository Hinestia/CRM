from django import forms

from .models import PersonalAccount


class PersonalAccountForm(forms.ModelForm):
    class Meta:
        model = PersonalAccount
        # registered_count не редактируется — считается автоматически по
        # числу действующих назначений в tenant_assignments (см. модель).
        fields = [
            "number", "unit", "status", "services",
            "opened_at", "closed_at", "notes",
        ]
        widgets = {
            "opened_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "closed_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "services": forms.CheckboxSelectMultiple,
        }
