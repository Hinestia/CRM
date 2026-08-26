from datetime import date

from celery import shared_task

from .services import generate_monthly_charges


@shared_task
def generate_monthly_charges_task():
    """Запускается Celery Beat на BILLING_GENERATION_DAY число месяца."""
    today = date.today()
    period = date(today.year, today.month, 1)
    charges = generate_monthly_charges(period)
    return f"Сформировано {len(charges)} начислений за {period:%m.%Y}"
