import pytest
from django.utils import timezone
from datetime import timedelta
from gamification.services import XPService
from gamification.models import UserProfile, Streak
from users.models import User

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="xpuser", password="pwd")

@pytest.mark.django_db
class TestXPService:
    def test_add_xp_and_level_up(self, test_user):
        XPService.add_xp(test_user, 150)
        profile = UserProfile.objects.get(user=test_user)
        assert profile.total_xp == 150
        assert profile.current_level == 2
        streak = Streak.objects.get(user=test_user)
        assert streak.current_streak == 1

    def test_streak_increment(self, test_user):
        streak, _ = Streak.objects.get_or_create(user=test_user)
        # Manually set last activity to yesterday
        streak.last_activity_date = timezone.now().date() - timedelta(days=1)
        streak.current_streak = 5
        streak.save()

        XPService.add_xp(test_user, 10)
        streak.refresh_from_db()
        assert streak.current_streak == 6
        assert streak.last_activity_date == timezone.now().date()

    def test_streak_reset_after_miss(self, test_user):
        streak, _ = Streak.objects.get_or_create(user=test_user)
        # Manually set last activity to 3 days ago
        streak.last_activity_date = timezone.now().date() - timedelta(days=3)
        streak.current_streak = 5
        streak.save()

        XPService.add_xp(test_user, 10)
        streak.refresh_from_db()
        assert streak.current_streak == 1
        assert streak.last_activity_date == timezone.now().date()

    def test_celery_recalculate_streaks(self, test_user):
        streak, _ = Streak.objects.get_or_create(user=test_user)
        streak.last_activity_date = timezone.now().date() - timedelta(days=2)
        streak.current_streak = 5
        streak.save()

        XPService.recalculate_streaks()
        streak.refresh_from_db()
        assert streak.current_streak == 0
