from django.db import models

from apps.billing.models import Charge


def receipt_upload_path(instance, filename):
    charge = instance.charge
    return f"receipts/{charge.period:%Y/%m}/{charge.account.number}.pdf"


class Receipt(models.Model):
    """Сформированная печатная квитанция (PDF) по одному начислению."""

    charge = models.OneToOneField(
        Charge, on_delete=models.CASCADE, related_name="receipt", verbose_name="Начисление"
    )
    file = models.FileField("Файл квитанции", upload_to=receipt_upload_path)

    generated_at = models.DateTimeField("Сформирована", auto_now_add=True)
    generated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True, blank=True,
        verbose_name="Кем сформирована",
    )
    emailed_at = models.DateTimeField("Отправлена по email", null=True, blank=True)

    class Meta:
        verbose_name = "Квитанция"
        verbose_name_plural = "Квитанции"
        ordering = ("-generated_at",)

    def __str__(self):
        return f"Квитанция ЛС №{self.charge.account.number} за {self.charge.period:%m.%Y}"
