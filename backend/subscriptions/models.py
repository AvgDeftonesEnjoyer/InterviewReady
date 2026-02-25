from django.db import models
from django.conf import settings
from django.utils import timezone

class Subscription(models.Model):
    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
        ('PRO_PLUS', 'Pro Plus'),
    )
    PROVIDER_CHOICES = (
        ('STRIPE', 'Stripe'),
        ('APPLE', 'Apple'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELED', 'Canceled'),
    )
    BILLING_CYCLE_CHOICES = (
        ('monthly', 'Monthly'),
        ('annual',  'Annual'),
    )
    PAYMENT_PROVIDER_CHOICES = (
        ('none',        'None'),
        ('stripe',      'Stripe (Android)'),
        ('apple',       'Apple IAP (iOS)'),
        ('revenuecat',  'RevenueCat'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, null=True, blank=True)
    provider_subscription_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
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
        choices=PAYMENT_PROVIDER_CHOICES,
        default='none'
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
        if self.status != 'ACTIVE':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            # Auto-expire if past expiry date
            self.status = 'EXPIRED'
            self.save(update_fields=['status'])
            return False
        return True

    @property
    def is_active(self):
        """Compatibility property for new payment system."""
        return self.status == 'ACTIVE' and self.is_valid

    @property
    def price(self):
        prices = {
            'FREE':     0,
            'PRO':      5,
            'PRO_PLUS': 10,
        }
        return prices.get(self.plan, 0)
