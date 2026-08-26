from datetime import date

from django.core.management.base import BaseCommand

from apps.billing.services import generate_monthly_charges


class Command(BaseCommand):
    help = (
        "Формирует начисления по всем активным лицевым счетам за указанный период. "
        "Без аргументов используется текущий месяц (год-месяц из --period или сегодня)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--period", type=str, default=None,
            help="Период в формате YYYY-MM-DD или YYYY-MM (используется первое число месяца)",
        )

    def handle(self, *args, **options):
        raw_period = options["period"]
        if raw_period:
            parts = [int(p) for p in raw_period.split("-")]
            year, month = parts[0], parts[1]
        else:
            today = date.today()
            year, month = today.year, today.month
        period = date(year, month, 1)

        charges = generate_monthly_charges(period)
        self.stdout.write(self.style.SUCCESS(
            f"Сформировано начислений: {len(charges)} за период {period:%m.%Y}"
        ))
