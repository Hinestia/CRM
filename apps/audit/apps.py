from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Журнал аудита"

    def ready(self):
        from .signals import connect_audit_signals

        connect_audit_signals()
