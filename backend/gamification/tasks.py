from celery import shared_task
from django.core.management import call_command
from .services import XPService

@shared_task
def recalculate_streaks_task():
    XPService.recalculate_streaks()

@shared_task
def generate_daily_challenges_task():
    call_command('generate_daily_challenges')
