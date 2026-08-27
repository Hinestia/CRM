from pathlib import Path

from django.core.files import File
from django.db import migrations

STARTER_TEMPLATE = (
    Path(__file__).resolve().parent.parent / "starter_templates" / "default_contract_template.docx"
)


def seed_template(apps, schema_editor):
    ContractTemplate = apps.get_model("contracts", "ContractTemplate")
    if ContractTemplate.objects.exists():
        return
    if not STARTER_TEMPLATE.exists():
        return
    template = ContractTemplate(name="Типовой договор найма", is_active=True)
    with open(STARTER_TEMPLATE, "rb") as f:
        template.file.save(STARTER_TEMPLATE.name, File(f), save=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("contracts", "0003_contracttemplate_generatedcontractfile")]
    operations = [migrations.RunPython(seed_template, noop_reverse)]
