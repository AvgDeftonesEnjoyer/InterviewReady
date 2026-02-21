import pytest
from django.utils import timezone
from datetime import timedelta
from gamification.services import XPService
from gamification.models import UserProfile
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
        assert profile.streak_days == 1

    def test_streak_increment(self, test_user):
        profile = XPService.get_or_create_profile(test_user)
        # Manually set last activity to yesterday
        profile.last_activity_date = timezone.now().date() - timedelta(days=1)
        profile.streak_days = 5
        profile.save()

        XPService.add_xp(test_user, 10)
        profile.refresh_from_db()
        assert profile.streak_days == 6
        assert profile.last_activity_date == timezone.now().date()

    def test_streak_reset_after_miss(self, test_user):
        profile = XPService.get_or_create_profile(test_user)
        # Manually set last activity to 3 days ago
        profile.last_activity_date = timezone.now().date() - timedelta(days=3)
        profile.streak_days = 5
        profile.save()

        XPService.add_xp(test_user, 10)
        profile.refresh_from_db()
        assert profile.streak_days == 1
        assert profile.last_activity_date == timezone.now().date()

    def test_celery_recalculate_streaks(self, test_user):
        profile = XPService.get_or_create_profile(test_user)
        profile.last_activity_date = timezone.now().date() - timedelta(days=2)
        profile.streak_days = 5
        profile.save()

        XPService.recalculate_streaks()
        profile.refresh_from_db()
        assert profile.streak_days == 0
