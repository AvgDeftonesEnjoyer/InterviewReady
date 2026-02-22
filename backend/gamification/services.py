from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Streak
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
        profile.save()
        
        # update last activity and streak
        streak, _ = Streak.objects.get_or_create(user=user)
        today = timezone.now().date()
        if streak.last_activity_date != today:
            if streak.last_activity_date == today - timedelta(days=1):
                streak.current_streak += 1
            elif streak.last_activity_date is None or streak.last_activity_date < today - timedelta(days=1):
                # Missed a day or first activity
                streak.current_streak = 1
                
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            
            streak.last_activity_date = today
            streak.save()

    @staticmethod
    def recalculate_streaks():
        """
        To be run via Celery Beat every midnight.
        Resets streak to 0 for users who didn't practice yesterday.
        """
        yesterday = timezone.now().date() - timedelta(days=1)
        # Anyone whose last_activity_date is strictly before yesterday missed their streak
        Streak.objects.filter(last_activity_date__lt=yesterday).update(current_streak=0)
