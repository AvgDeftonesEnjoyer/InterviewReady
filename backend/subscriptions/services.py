from django.utils import timezone
from django.db import models
from .models import Subscription
from users.models import User

class SubscriptionService:
    @staticmethod
    def get_active_subscription(user: User) -> Subscription | None:
        return Subscription.objects.filter(
            user=user,
            status='ACTIVE'
        ).filter(
            # Either expires_at is null (lifetime) or it's in the future
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).order_by('-started_at').first()

    @staticmethod
    def is_pro(user: User) -> bool:
        if user.is_internal_tester:
            return True
        
        active_sub = SubscriptionService.get_active_subscription(user)
        if active_sub and active_sub.plan == 'PRO':
            return True
            
        return False

    @staticmethod
    def check_feature_access(user: User, feature_name: str) -> bool:
        """
        Generic feature access check.
        Can be extended later to handle specific 'feature_name' logic.
        For now, if it requires PRO and the user doesn't have it, returns False.
        """
        # Placeholder for specific feature logic.
        # By default, anything beyond FREE needs a PRO subscription or internal tester status
        return SubscriptionService.is_pro(user)
