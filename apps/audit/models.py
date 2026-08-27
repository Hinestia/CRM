from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "create", "Создание"
    UPDATE = "update", "Изменение"
    DELETE = "delete", "Удаление"


class AuditLogEntry(models.Model):
    """Журнал аудита действий сотрудников над ключевыми сущностями
    (начисления, тарифы, перерасчёты, лицевые счета, наниматели).

    Заполняется автоматически через сигналы (см. apps/audit/signals.py) —
    ручное создание записей не предполагается.
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="audit_entries",
        null=True, blank=True, verbose_name="Пользователь",
    )
    action = models.CharField("Действие", max_length=10, choices=AuditAction.choices)
    model_name = models.CharField("Модель", max_length=100)
    object_id = models.CharField("ID объекта", max_length=50)
    object_repr = models.CharField("Объект", max_length=255)
    changes = models.JSONField(
        "Изменения", default=dict, blank=True, encoder=DjangoJSONEncoder
    )
    timestamp = models.DateTimeField("Дата/время", auto_now_add=True)

    class Meta:
        verbose_name = "Запись аудита"
        verbose_name_plural = "Журнал аудита"
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.model_name} #{self.object_id} — {self.user}"
