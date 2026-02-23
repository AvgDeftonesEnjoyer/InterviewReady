from datetime import date
from .models import InterviewSession

# Daily interview limits per plan (from spec)
DAILY_LIMITS = {
    'FREE': 1,      # 1 interview per day
    'PRO': 5,       # $5/mo - 5 interviews per day
    'PRO_PLUS': 10, # $10/mo - 10 interviews per day
}


def get_user_plan(user) -> str:
    """Returns user's plan: 'FREE', 'PRO', or 'PRO_PLUS'."""
    from subscriptions.services import SubscriptionService
    return SubscriptionService.get_plan(user)


def get_quota(user) -> dict:
    plan = get_user_plan(user)
    limit = DAILY_LIMITS[plan]
    used = InterviewSession.objects.filter(
        user=user,
        started_at__date=date.today()
    ).count()
    remaining = max(0, limit - used)
    return {
        'plan': plan,
        'limit': limit,
        'used': used,
        'remaining': remaining,
        'can_start': remaining > 0,
    }
