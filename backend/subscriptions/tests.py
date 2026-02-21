import pytest
from subscriptions.services import SubscriptionService
from subscriptions.models import Subscription
from users.models import User

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", email="test@test.com", password="pwd")

@pytest.fixture
def internal_tester(db):
    return User.objects.create_user(username="tester", email="tester@test.com", password="pwd", is_internal_tester=True)

@pytest.mark.django_db
class TestSubscriptionService:
    def test_is_pro_internal_tester(self, internal_tester):
        assert SubscriptionService.is_pro(internal_tester) is True

    def test_is_pro_free_user(self, test_user):
        assert SubscriptionService.is_pro(test_user) is False

    def test_is_pro_active_subscription(self, test_user):
        Subscription.objects.create(user=test_user, plan='PRO', status='ACTIVE')
        assert SubscriptionService.is_pro(test_user) is True

    def test_is_pro_expired_subscription(self, test_user):
        Subscription.objects.create(user=test_user, plan='PRO', status='EXPIRED')
        assert SubscriptionService.is_pro(test_user) is False
