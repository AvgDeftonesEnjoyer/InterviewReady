from datetime import date, timedelta
from django.utils import timezone
import pytz
from .models import InterviewSession

from subscriptions.models import SubscriptionPlan

# Fallback limits if DB has not been seeded yet
FALLBACK_DAILY_LIMITS = {
    SubscriptionPlan.PlanType.FREE: 1,      # 1 interview per day
    SubscriptionPlan.PlanType.PRO: 5,       # $5/mo - 5 interviews per day
    SubscriptionPlan.PlanType.PRO_PLUS: 10, # $10/mo - 10 interviews per day
}


def get_user_plan(user) -> str:
    """Returns user's plan: 'FREE', 'PRO', or 'PRO_PLUS'."""
    from subscriptions.services import SubscriptionService
    return SubscriptionService.get_plan(user)


def get_user_timezone(user) -> pytz.timezone:
    """
    Get user's timezone from profile, default to UTC.
    TIMEZONE: Uses user's timezone for accurate daily quota calculation.
    """
    try:
        tz_name = user.profile.timezone if hasattr(user, 'profile') and user.profile else 'UTC'
        return pytz.timezone(tz_name)
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        return pytz.UTC


def get_today_in_user_timezone(user) -> date:
    """
    Get today's date in the user's timezone.
    This ensures quota resets at midnight in user's local time.
    """
    user_tz = get_user_timezone(user)
    now = timezone.now().astimezone(user_tz)
    return now.date()


def get_quota(user) -> dict:
    """
    Calculate user's interview quota.
    TIMEZONE: Uses user's local timezone for accurate daily limits.
    """
    plan = get_user_plan(user)
    
    try:
        plan_config = SubscriptionPlan.objects.get(name=plan)
        limit = plan_config.daily_interview_limit
    except SubscriptionPlan.DoesNotExist:
        limit = FALLBACK_DAILY_LIMITS.get(plan, 1)
    
    # Get today's date in user's timezone
    today = get_today_in_user_timezone(user)
    
    # Count interviews started today in user's timezone
    used = InterviewSession.objects.filter(
        user=user,
        started_at__date=today
    ).count()
    
    remaining = max(0, limit - used)
    
    return {
        'plan': plan,
        'limit': limit,
        'used': used,
        'remaining': remaining,
        'can_start': remaining > 0,
        'timezone': str(get_user_timezone(user)),
    }
