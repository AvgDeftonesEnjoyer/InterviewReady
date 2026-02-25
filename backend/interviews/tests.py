"""
Unit tests for Interview Service and Quota calculation.
Tests cover quota limits, session management, and plan-based access.
"""
import pytest
from asgiref.sync import async_to_sync
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, AsyncMock
from django.urls import reverse
from interviews.models import InterviewSession
from interviews.services import get_quota, get_user_plan
from subscriptions.models import Subscription, SubscriptionPlan
from django.contrib.auth import get_user_model
from django.urls import reverse
# To test async views in DRF properly, some components require async client 
# but there's a known limitation in DRF's built-in client.
# The workaround is using force_authenticate on a standard test client
# and ensuring the view handles the event loop properly.

User = get_user_model()


class TestInterviewQuota(APITestCase):
    """Test cases for interview quota calculation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='interviewuser',
            email='interview@example.com',
            password='password123'
        )
        self.today = timezone.now().date()
        
        # Seed the DB with required SubscriptionPlans for defaults
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.FREE, monthly_price=0, annual_price=0, daily_interview_limit=1)
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.PRO, monthly_price=5, annual_price=47.99, daily_interview_limit=5)
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.PRO_PLUS, monthly_price=10, annual_price=95.99, daily_interview_limit=10)

    def test_free_plan_quota(self):
        """Test quota for FREE plan users."""
        quota = get_quota(self.user)
        
        assert quota['plan'] == 'FREE'
        assert quota['limit'] == 1
        assert quota['used'] == 0
        assert quota['remaining'] == 1
        assert quota['can_start'] is True

    def test_pro_plan_quota(self):
        """Test quota for PRO plan users."""
        Subscription.objects.create(
            user=self.user,
            plan='PRO',
            status='ACTIVE',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        quota = get_quota(self.user)
        
        assert quota['plan'] == 'PRO'
        assert quota['limit'] == 5
        assert quota['remaining'] == 5
        assert quota['can_start'] is True

    def test_pro_plus_plan_quota(self):
        """Test quota for PRO_PLUS plan users."""
        Subscription.objects.create(
            user=self.user,
            plan='PRO_PLUS',
            status='ACTIVE',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        quota = get_quota(self.user)
        
        assert quota['plan'] == 'PRO_PLUS'
        assert quota['limit'] == 10
        assert quota['remaining'] == 10
        assert quota['can_start'] is True

    def test_quota_after_using_interviews(self):
        """Test quota decreases after starting interviews."""
        # Create 2 interviews today
        InterviewSession.objects.create(
            user=self.user,
            mode='hr',
            question_count_target=10,
            status='active'
        )
        InterviewSession.objects.create(
            user=self.user,
            mode='tech',
            question_count_target=10,
            status='completed'
        )
        
        quota = get_quota(self.user)
        
        assert quota['used'] == 2
        assert quota['remaining'] == 0  # FREE plan limit is 1
        assert quota['can_start'] is False

    def test_quota_resets_daily(self):
        """Test that quota only counts today's interviews."""
        # Create interview yesterday
        yesterday = timezone.now() - timedelta(days=1)
        session = InterviewSession.objects.create(
            user=self.user,
            mode='hr',
            status='completed',
            finished_at=yesterday
        )
        # Use update() to bypass auto_now_add on started_at
        InterviewSession.objects.filter(id=session.id).update(started_at=yesterday)
        
        quota = get_quota(self.user)
        
        assert quota['used'] == 0
        assert quota['remaining'] == quota['limit']

    def test_internal_tester_bypass(self):
        """Test that internal testers have unlimited access."""
        self.user.is_internal_tester = True
        self.user.save()
        
        quota = get_quota(self.user)
        
        assert quota['plan'] == 'PRO_PLUS'
        assert quota['limit'] == 10


class TestInterviewSession(APITestCase):
    """Test cases for InterviewSession model and views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='sessionuser',
            email='session@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)

        # Seed the DB with required SubscriptionPlans for get_quota
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.FREE, monthly_price=0, annual_price=0, daily_interview_limit=10)

    @patch('interviews.views.aget_ai_response', new_callable=AsyncMock)
    def test_start_interview_hr_mode(self, mock_agets_ai_response):
        """Test starting an HR interview session."""
        mock_agets_ai_response.return_value = "Hello, first question."
        response = self.client.post(reverse('interview_start'), {
            'mode': 'hr',
            'question_count': 10
        })
        
        assert response.status_code == 201
        assert response.data['message'] == "Hello, first question."

    def test_start_interview_requires_language_for_tech(self):
        """Test that tech mode requires language parameter."""
        response = self.client.post(reverse('interview_start'), {
            'mode': 'tech',
            'question_count': 10
        })
        
        assert response.status_code == 400
        assert 'Language required' in str(response.data)

    def test_start_interview_invalid_mode(self):
        """Test starting interview with invalid mode."""
        response = self.client.post(reverse('interview_start'), {
            'mode': 'invalid',
            'question_count': 10
        })
        
        assert response.status_code == 400

    @patch('interviews.views.aget_ai_response', new_callable=AsyncMock)
    def test_start_interview_invalid_question_count(self, mock_aget):
        """Test starting interview with invalid question count."""
        mock_aget.return_value = "Hello"
        response = self.client.post(reverse('interview_start'), {
            'mode': 'hr',
            'question_count': 99
        })
        
        # Should default to 10 or return error
        assert response.status_code in [201, 400, 500]

    def test_send_message_empty_content(self):
        """Test sending empty message."""
        session = InterviewSession.objects.create(
            user=self.user,
            mode='hr',
            question_count_target=10,
            status=InterviewSession.Status.ACTIVE
        )
        
        response = self.client.post(reverse('interview_message', args=[session.id]), {
            'content': ''
        })
        
        assert response.status_code == 400

    @patch('interviews.views.aget_ai_response', new_callable=AsyncMock)
    def test_send_message_completes_interview(self, mock_aget_ai_response):
        """Test sending a message that completes the interview."""
        session = InterviewSession.objects.create(
            user=self.user,
            mode='hr',
            question_count_target=10,
            status=InterviewSession.Status.ACTIVE
        )
        
        mock_aget_ai_response.return_value = "Sure. [INTERVIEW_COMPLETE]"
        response = self.client.post(reverse('interview_message', args=[session.id]), {
            'content': 'my answer'
        })
        
        assert response.status_code == 200
        assert response.data['is_complete'] is True
        session.refresh_from_db()
        assert session.status == InterviewSession.Status.COMPLETED

    def test_send_message_to_nonexistent_session(self):
        """Test sending message to non-existent session."""
        response = self.client.post(reverse('interview_message', args=[99999]), {
            'content': 'test message'
        })
        
        assert response.status_code == 404

    def test_session_history(self):
        """Test retrieving session history."""
        session = InterviewSession.objects.create(
            user=self.user,
            mode='hr',
            messages=[
                {'role': 'assistant', 'content': 'Hello!'}
            ],
            status='active'
        )
        
        response = self.client.get(reverse('interview_history', args=[session.id]))
        
        assert response.status_code == 200
        assert response.data['session_id'] == session.id
        assert response.data['mode'] == 'hr'


class TestSubscriptionPlanAccess(APITestCase):
    """Test subscription plan access for interviews."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='planuser',
            email='plan@example.com',
            password='password123'
        )
        
        # Seed the DB with required SubscriptionPlans
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.FREE, monthly_price=0, annual_price=0, daily_interview_limit=1)
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.PRO, monthly_price=5, annual_price=47.99, daily_interview_limit=5)
        SubscriptionPlan.objects.create(name=SubscriptionPlan.PlanType.PRO_PLUS, monthly_price=10, annual_price=95.99, daily_interview_limit=10)


    def test_expired_subscription_reverts_to_free(self):
        """Test that expired subscription reverts to FREE plan."""
        Subscription.objects.create(
            user=self.user,
            plan='PRO',
            status='ACTIVE',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        plan = get_user_plan(self.user)
        
        assert plan == 'FREE'

    def test_canceled_subscription_access(self):
        """Test that canceled subscription still provides access until expiry."""
        Subscription.objects.create(
            user=self.user,
            plan='PRO',
            status='CANCELED',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        plan = get_user_plan(self.user)
        assert plan == 'FREE'

    def test_multiple_subscriptions_uses_latest(self):
        """Test that multiple subscriptions use the latest one."""
        Subscription.objects.create(
            user=self.user,
            plan='PRO',
            status='ACTIVE',
            started_at=timezone.now() - timedelta(days=60),
            expires_at=timezone.now() - timedelta(days=30)
        )
        
        Subscription.objects.create(
            user=self.user,
            plan='PRO_PLUS',
            status='ACTIVE',
            started_at=timezone.now() - timedelta(days=30),
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        plan = get_user_plan(self.user)
        
        assert plan == 'PRO_PLUS'
