from django import forms

from .models import Payment, Recalculation


class RecalculationForm(forms.ModelForm):
    class Meta:
        model = Recalculation
        fields = ["service", "period", "amount", "reason", "comment"]
        widgets = {
            "period": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["date", "amount", "reference"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class GeneratePeriodForm(forms.Form):
    period = forms.DateField(
        label="Период", widget=forms.DateInput(attrs={"type": "month"}, format="%Y-%m"),
        input_formats=["%Y-%m"],
    )
