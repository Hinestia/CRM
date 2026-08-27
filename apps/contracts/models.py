from datetime import date

from django.conf import settings
from django.db import models

from apps.accounts.models import PersonalAccount


class Contract(models.Model):
    """Договор (найма/аренды/обслуживания), привязанный к лицевому счёту."""

    account = models.ForeignKey(
        PersonalAccount,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Лицевой счёт",
    )
    number = models.CharField("Номер договора", max_length=50)
    signed_date = models.DateField("Дата заключения")
    end_date = models.DateField("Дата окончания", null=True, blank=True)

    responsible_employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="responsible_contracts",
        verbose_name="Ответственные сотрудники",
        blank=True,
        help_text="Получат уведомление за месяц до окончания договора",
    )

    expiry_notified_at = models.DateTimeField(
        "Уведомление отправлено", null=True, blank=True, editable=False
    )

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
        unique_together = ("account", "number")
        ordering = ("-signed_date",)
        indexes = [models.Index(fields=["end_date"])]

    def __str__(self):
        return f"Договор №{self.number} (ЛС {self.account.number})"

    @property
    def is_active(self):
        return self.end_date is None or self.end_date >= date.today()


def contract_template_upload_path(instance, filename):
    return f"contract_templates/{filename}"


class ContractTemplate(models.Model):
    """Шаблон печатной формы договора (.docx) с плейсхолдерами docxtpl
    (например {{ tenant_full_name }}, {{ account_number }} — см. DESIGN.md).

    Хранится как обычный файл, редактируется в Word без участия
    разработчика; активным должен быть только один шаблон — именно он
    используется кнопкой «Сформировать договор» на карточке ЛС."""

    name = models.CharField("Название шаблона", max_length=150)
    file = models.FileField("Файл шаблона (.docx)", upload_to=contract_template_upload_path)
    is_active = models.BooleanField(
        "Активный шаблон", default=True,
        help_text="Используется при формировании договора. Активным должен быть только один.",
    )
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Шаблон договора"
        verbose_name_plural = "Шаблоны договора"
        ordering = ("-is_active", "-updated_at")

    def __str__(self):
        return self.name


def generated_contract_upload_path(instance, filename):
    return f"contracts/{instance.contract.account.number}/{instance.contract.number}.pdf"


class GeneratedContractFile(models.Model):
    """Сформированный из шаблона PDF договора. Перегенерация (кнопка
    «Сформировать договор» нажата повторно) перезаписывает файл — история
    версий не хранится, актуален всегда последний вариант."""

    contract = models.OneToOneField(
        Contract, on_delete=models.CASCADE, related_name="generated_file", verbose_name="Договор"
    )
    file = models.FileField("PDF договора", upload_to=generated_contract_upload_path)
    generated_at = models.DateTimeField("Сформирован", auto_now_add=True)
    generated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="+", null=True, blank=True,
        verbose_name="Кем сформирован",
    )

    class Meta:
        verbose_name = "Сформированный договор (PDF)"
        verbose_name_plural = "Сформированные договоры (PDF)"

    def __str__(self):
        return f"PDF договора №{self.contract.number}"
