from django.db.models.signals import post_delete, post_save, pre_save

from .middleware import get_current_user
from .models import AuditAction, AuditLogEntry

# Модели, изменения которых логируются в журнал аудита.
TRACKED_MODELS = [
    "billing.Charge",
    "billing.ChargeLine",
    "billing.Recalculation",
    "billing.Payment",
    "services.Tariff",
    "accounts.PersonalAccount",
    "tenants.TenantAccountAssignment",
]

_IGNORED_FIELDS = {"updated_at", "created_at"}


def _current_user_or_none():
    user = get_current_user()
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    return user


def _field_values(instance):
    return {
        f.name: f.value_from_object(instance)
        for f in instance._meta.fields
        if f.name not in _IGNORED_FIELDS
    }


def _pre_save_handler(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._audit_old_values = _field_values(sender.objects.get(pk=instance.pk))
        except sender.DoesNotExist:
            instance._audit_old_values = None
    else:
        instance._audit_old_values = None


def _post_save_handler(sender, instance, created, **kwargs):
    new_values = _field_values(instance)
    old_values = getattr(instance, "_audit_old_values", None)

    if created:
        action = AuditAction.CREATE
        changes = {k: [None, v] for k, v in new_values.items()}
    else:
        if old_values is None:
            return
        changes = {
            k: [old_values.get(k), v] for k, v in new_values.items() if old_values.get(k) != v
        }
        if not changes:
            return
        action = AuditAction.UPDATE

    AuditLogEntry.objects.create(
        user=_current_user_or_none(),
        action=action,
        model_name=f"{sender._meta.app_label}.{sender.__name__}",
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes=changes,
    )


def _post_delete_handler(sender, instance, **kwargs):
    AuditLogEntry.objects.create(
        user=_current_user_or_none(),
        action=AuditAction.DELETE,
        model_name=f"{sender._meta.app_label}.{sender.__name__}",
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes={},
    )


def connect_audit_signals():
    from django.apps import apps

    for label in TRACKED_MODELS:
        model = apps.get_model(label)
        pre_save.connect(_pre_save_handler, sender=model, weak=False)
        post_save.connect(_post_save_handler, sender=model, weak=False)
        post_delete.connect(_post_delete_handler, sender=model, weak=False)
