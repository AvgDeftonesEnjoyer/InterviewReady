from datetime import date
from .models import InterviewSession

DAILY_LIMITS = {
    'FREE': 2,
    'PRO': 10,
}


def get_user_plan(user) -> str:
    """Returns the user's current plan: 'FREE' or 'PRO'."""
    active_sub = user.subscriptions.filter(status='ACTIVE').order_by('-started_at').first()
    if active_sub and active_sub.plan == 'PRO':
        return 'PRO'
    return 'FREE'


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
