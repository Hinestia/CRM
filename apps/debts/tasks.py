from celery import shared_task

from .services import accrue_penalties


@shared_task
def accrue_penalties_task():
    """Ежедневный пересчёт пени по просроченным начислениям (Celery Beat)."""
    accruals = accrue_penalties()
    return f"Начислено пени по {len(accruals)} лицевым счетам"
