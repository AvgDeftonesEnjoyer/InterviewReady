from django.db import models
from django.conf import settings
from django.utils import timezone

class SubscriptionPlan(models.Model):
    """
    Dynamic pricing and feature configuration for Subscription Plans.
    Allows changing prices via Django Admin instead of hardcoding in settings.py.
    """
    class PlanType(models.TextChoices):
        FREE = 'FREE', 'Free'
        PRO = 'PRO', 'Pro'
        PRO_PLUS = 'PRO_PLUS', 'Pro Plus'

    name = models.CharField(max_length=10, choices=PlanType.choices, unique=True)
    monthly_price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Monthly price in USD")
    annual_price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Annual price in USD")
    daily_interview_limit = models.IntegerField(default=1, help_text="Number of mock interviews per day")
    is_active = models.BooleanField(default=True)
    
    # Optional Stripe/Apple IDs can be stored here for easy syncing later
    stripe_monthly_price_id = models.CharField(max_length=100, blank=True, default='')
    stripe_annual_price_id = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.get_name_display()} (${self.monthly_price}/mo)"


class Subscription(models.Model):
    class Plan(models.TextChoices):
        FREE = 'FREE', 'Free'
        PRO = 'PRO', 'Pro'
        PRO_PLUS = 'PRO_PLUS', 'Pro Plus'

    class Provider(models.TextChoices):
        STRIPE = 'STRIPE', 'Stripe'
        APPLE = 'APPLE', 'Apple'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELED = 'CANCELED', 'Canceled'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        ANNUAL = 'annual', 'Annual'

    class PaymentProvider(models.TextChoices):
        NONE = 'none', 'None'
        STRIPE = 'stripe', 'Stripe (Android)'
        APPLE = 'apple', 'Apple IAP (iOS)'
        REVENUECAT = 'revenuecat', 'RevenueCat'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=10, choices=Plan.choices, default=Plan.FREE)
    provider = models.CharField(max_length=20, choices=Provider.choices, null=True, blank=True)
    provider_subscription_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Stripe (for Android)
    stripe_customer_id      = models.CharField(max_length=100, blank=True, default='')
    stripe_subscription_id  = models.CharField(max_length=100, blank=True, default='')

    # RevenueCat (shared identifier iOS+Android)
    revenuecat_user_id = models.CharField(max_length=100, blank=True, default='')

    # Where the subscription came from
    payment_provider = models.CharField(
        max_length=20,
        choices=PaymentProvider.choices,
        default=PaymentProvider.NONE
    )

    class Meta:
        # OPTIMIZATION: Add indexes for frequently filtered fields
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'plan']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['provider', 'provider_subscription_id']),
            models.Index(fields=['stripe_subscription_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"

    @property
    def is_valid(self):
        """Check if subscription is currently valid. Pure read — no DB writes."""
        if self.status != self.Status.ACTIVE:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            # Note: Expired subscriptions are cleaned up by a Celery task, not here.
            return False
        return True

    @property
    def is_active(self):
        """Compatibility property for new payment system."""
        return self.status == self.Status.ACTIVE and self.is_valid

    @property
    def price(self):
        """
        Dynamically fetches price from the SubscriptionPlan model.
        Falls back to hardcoded if DB model is not populated.
        """
        try:
            plan_obj = SubscriptionPlan.objects.get(name=self.plan)
            return plan_obj.monthly_price if self.billing_cycle == self.BillingCycle.MONTHLY else plan_obj.annual_price
        except SubscriptionPlan.DoesNotExist:
            # Fallback for when migrations are freshly run or DB is missing data
            prices = {
                self.Plan.FREE:     0,
                self.Plan.PRO:      4.99 if self.billing_cycle == self.BillingCycle.MONTHLY else 47.99,
                self.Plan.PRO_PLUS: 9.99 if self.billing_cycle == self.BillingCycle.MONTHLY else 95.99,
            }
            return prices.get(self.plan, 0)
