from django import forms

from .models import PenaltySettings


class PenaltySettingsForm(forms.ModelForm):
    class Meta:
        model = PenaltySettings
        fields = ["name", "grace_period_days", "rate_per_day", "is_active"]
