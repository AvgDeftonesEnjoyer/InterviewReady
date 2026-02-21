from django.db import models
from django.conf import settings

class Subscription(models.Model):
    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, null=True, blank=True)
    provider_subscription_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"
