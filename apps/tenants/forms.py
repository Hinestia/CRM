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
    class Meta:
        model = TenantAccountAssignment
        fields = ["tenant", "is_primary", "start_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
