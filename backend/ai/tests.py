import pytest
from django.utils import timezone
from datetime import timedelta
from ai.services import AIUsageService
from ai.models import AIUsage
from users.models import User
from subscriptions.models import Subscription

@pytest.fixture
def free_user(db):
    return User.objects.create_user(username="free", password="pwd")

@pytest.fixture
def pro_user(db):
    u = User.objects.create_user(username="pro", password="pwd")
    Subscription.objects.create(user=u, plan='PRO', status='ACTIVE')
    return u

@pytest.mark.django_db
class TestAIUsageService:
    def test_free_user_can_use_within_limits(self, free_user):
        assert AIUsageService.can_use_ai(free_user) is True
        
        usage = AIUsageService.get_or_create_usage(free_user)
        usage.used_today = 5
        usage.save()
        
        assert AIUsageService.can_use_ai(free_user) is False

    def test_pro_user_unlimited(self, pro_user):
        usage = AIUsageService.get_or_create_usage(pro_user)
        usage.used_today = 100
        usage.save()
        
        assert AIUsageService.can_use_ai(pro_user) is True

    def test_reset_if_new_day(self, free_user):
        usage = AIUsageService.get_or_create_usage(free_user)
        usage.used_today = 5
        usage.last_reset = timezone.now().date() - timedelta(days=1)
        usage.save()
        
        assert AIUsageService.can_use_ai(free_user) is True
        usage.refresh_from_db()
        assert usage.used_today == 0
        assert usage.last_reset == timezone.now().date()
