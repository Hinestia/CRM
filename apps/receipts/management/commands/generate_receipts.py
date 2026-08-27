from datetime import date

from django.core.management.base import BaseCommand

from apps.receipts.services import generate_receipts_for_period


class Command(BaseCommand):
    help = "Массово формирует PDF-квитанции по всем начислениям за указанный период."

    def add_arguments(self, parser):
        parser.add_argument(
            "--period", type=str, required=True, help="Период в формате YYYY-MM"
        )

    def handle(self, *args, **options):
        year, month = (int(p) for p in options["period"].split("-")[:2])
        period = date(year, month, 1)
        receipts = generate_receipts_for_period(period)
        self.stdout.write(self.style.SUCCESS(
            f"Сформировано квитанций: {len(receipts)} за период {period:%m.%Y}"
        ))
