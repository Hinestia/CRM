from celery import shared_task

from .services import catch_up_charges


@shared_task
def catch_up_charges_task():
    """Запускается Celery Beat ежедневно (см. CELERY_BEAT_SCHEDULE).

    Не привязана жёстко к BILLING_GENERATION_DAY: если сервер/Celery был
    недоступен в нужный день (или несколько месяцев подряд), эта задача
    сама донасчитает все пропущенные периоды при следующем успешном
    запуске — см. apps.billing.services.catch_up_charges.
    """
    charges = catch_up_charges()
    return f"Донасчитано {len(charges)} начислений"
