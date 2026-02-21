from celery import shared_task
from .services import AIUsageService

@shared_task
def reset_daily_ai_usage_task():
    AIUsageService.reset_all_daily_usage()
