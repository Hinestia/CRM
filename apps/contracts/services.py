"""Генерация печатной формы договора (PDF) из шаблона .docx.

Подход: docxtpl рендерит шаблон .docx (Jinja-плейсхолдеры вида
{{ account_number }}) с автоподставленными данными договора, затем
LibreOffice в headless-режиме конвертирует результат в PDF — так итоговый
файл выглядит ровно как оригинальный .docx-шаблон, включая любое
форматирование, которое юрист/бухгалтер сделал в Word, без необходимости
верстать документ средствами Python (в отличие от ReportLab).

Шаблон правится в Word и загружается через админку (ContractTemplate) —
изменить текст договора можно без изменения кода.
"""

import subprocess
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile

from .models import Contract, ContractTemplate, GeneratedContractFile


class NoActiveContractTemplate(Exception):
    """Нет активного шаблона договора — сначала нужно загрузить его в админке."""


def _contract_context(contract: Contract) -> dict:
    account = contract.account
    unit = account.unit
    house = unit.house
    responsible = account.current_responsible
    services = account.services.filter(is_active=True).order_by("sort_order", "name")

    return {
        "contract_number": contract.number,
        "signed_date": contract.signed_date.strftime("%d.%m.%Y"),
        "end_date": contract.end_date.strftime("%d.%m.%Y") if contract.end_date else "бессрочно",
        "account_number": account.number,
        "tenant_full_name": responsible.full_name if responsible else "",
        "tenant_passport": (
            f"{responsible.passport_series} {responsible.passport_number}".strip()
            if responsible else ""
        ),
        "tenant_passport_issued_by": responsible.passport_issued_by if responsible else "",
        "tenant_passport_issued_date": (
            responsible.passport_issued_date.strftime("%d.%m.%Y")
            if responsible and responsible.passport_issued_date else ""
        ),
        "tenant_phone": responsible.phone if responsible else "",
        "address": f"{house}, кв./пом. {unit.number}",
        "area_total": str(unit.area_total),
        "area_billable": str(unit.billable_area),
        "services": ", ".join(s.name for s in services) or "—",
    }


def _convert_docx_to_pdf(docx_path: Path, out_dir: Path) -> Path:
    # Отдельный профиль LibreOffice на вызов: без этого параллельные
    # запросы конкурируют за единственный профиль пользователя контейнера
    # и падают с ошибкой "soffice уже запущен".
    profile_dir = out_dir / "lo_profile"
    result = subprocess.run(
        [
            "soffice", "--headless", "--invisible", "--nocrashreport", "--nodefault",
            "--nofirststartwizard", "--nologo", "--norestore",
            f"-env:UserInstallation=file://{profile_dir}",
            "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_path),
        ],
        capture_output=True, timeout=120,
    )
    pdf_path = out_dir / (docx_path.stem + ".pdf")
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(
            f"LibreOffice не смог сконвертировать договор в PDF: "
            f"{result.stderr.decode(errors='replace')}"
        )
    return pdf_path


def generate_contract_pdf(contract: Contract, user=None) -> GeneratedContractFile:
    from docxtpl import DocxTemplate  # импорт здесь — тяжёлая зависимость, нужна не везде

    template = ContractTemplate.objects.filter(is_active=True).first()
    if template is None:
        raise NoActiveContractTemplate

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        docx_path = tmp_dir / "contract.docx"

        doc = DocxTemplate(template.file)
        doc.render(_contract_context(contract))
        doc.save(docx_path)

        pdf_path = _convert_docx_to_pdf(docx_path, tmp_dir)
        pdf_bytes = pdf_path.read_bytes()

    generated, _ = GeneratedContractFile.objects.update_or_create(
        contract=contract, defaults={"generated_by": user},
    )
    filename = f"{contract.account.number}_{contract.number}.pdf"
    generated.file.save(filename, ContentFile(pdf_bytes), save=True)
    return generated
