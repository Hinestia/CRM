from django import forms

from .models import Tenant, TenantAccountAssignment


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            "last_name", "first_name", "middle_name", "phone", "email",
            "passport_series", "passport_number", "passport_issued_by", "passport_issued_date",
        ]
        widgets = {
            "passport_issued_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class TenantAccountAssignmentForm(forms.ModelForm):
    """Прописать на лицевой счёт уже существующего человека (выбор из списка)."""

    class Meta:
        model = TenantAccountAssignment
        fields = ["tenant", "is_primary", "start_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class AssignmentDetailsForm(forms.ModelForm):
    """Та же форма назначения, но без выбора нанимателя — используется вместе
    с TenantForm, когда человека сразу и заводят, и прописывают на ЛС."""

    is_primary = forms.BooleanField(
        label="Ответственный наниматель (основной плательщик)", required=False, initial=True,
    )

    class Meta:
        model = TenantAccountAssignment
        fields = ["is_primary", "start_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
