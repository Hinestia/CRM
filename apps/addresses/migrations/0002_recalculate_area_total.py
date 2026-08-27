from django.db import migrations
from django.db.models import F


def recalculate_area_total(apps, schema_editor):
    Unit = apps.get_model("addresses", "Unit")
    Unit.objects.update(
        area_total=F("area_living") + F("area_non_living") + F("area_balcony")
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("addresses", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(recalculate_area_total, noop_reverse),
    ]
