from celery import shared_task
from .services import XPService

@shared_task
def recalculate_streaks_task():
    XPService.recalculate_streaks()
