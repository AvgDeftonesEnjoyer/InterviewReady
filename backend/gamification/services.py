from django.utils import timezone
from datetime import timedelta
from .models import UserProfile
from users.models import User

class XPService:
    XP_PER_LEVEL = 100

    @staticmethod
    def get_or_create_profile(user: User) -> UserProfile:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def add_xp(user: User, amount: int):
        profile = XPService.get_or_create_profile(user)
        profile.total_xp += amount
        
        # update level
        profile.current_level = (profile.total_xp // XPService.XP_PER_LEVEL) + 1
        
        # update last activity and streak
        today = timezone.now().date()
        if profile.last_activity_date != today:
            if profile.last_activity_date == today - timedelta(days=1):
                profile.streak_days += 1
            elif profile.last_activity_date is None or profile.last_activity_date < today - timedelta(days=1):
                # Missed a day or first activity
                profile.streak_days = 1
            
            profile.last_activity_date = today

        profile.save()

    @staticmethod
    def recalculate_streaks():
        """
        To be run via Celery Beat every midnight.
        Resets streak to 0 for users who didn't practice yesterday.
        """
        yesterday = timezone.now().date() - timedelta(days=1)
        # Anyone whose last_activity_date is strictly before yesterday missed their streak
        UserProfile.objects.filter(last_activity_date__lt=yesterday).update(streak_days=0)
