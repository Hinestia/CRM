from django import forms

from .models import Meter, MeterReading


class MeterForm(forms.ModelForm):
    class Meta:
        model = Meter
        fields = ["service", "serial_number", "installed_date", "verification_date", "next_verification_date"]
        widgets = {
            "installed_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "verification_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "next_verification_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class MeterReadingForm(forms.ModelForm):
    period = forms.DateField(
        label="Период", widget=forms.DateInput(attrs={"type": "month"}, format="%Y-%m"), input_formats=["%Y-%m"],
    )

    class Meta:
        model = MeterReading
        fields = ["period", "value"]
