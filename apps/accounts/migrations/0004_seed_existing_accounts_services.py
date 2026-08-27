from django.db import migrations


def seed_services(apps, schema_editor):
    """До этой миграции начисления шли по ВСЕМ активным услугам для ЛЮБОГО
    лицевого счёта (см. apps.billing.services.generate_charge_for_account,
    было: services = services or Service.objects.filter(is_active=True)).
    Теперь список услуг явный и хранится на самом ЛС — чтобы у уже
    настроенных счетов начисления не пропали молча, заполняем его тем же
    набором услуг, что действовал раньше (все активные на момент миграции).
    """
    PersonalAccount = apps.get_model("accounts", "PersonalAccount")
    Service = apps.get_model("services", "Service")

    active_service_ids = list(Service.objects.filter(is_active=True).values_list("pk", flat=True))
    if not active_service_ids:
        return

    for account in PersonalAccount.objects.all():
        account.services.add(*active_service_ids)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_personalaccount_services"),
    ]

    operations = [
        migrations.RunPython(seed_services, noop_reverse),
    ]
