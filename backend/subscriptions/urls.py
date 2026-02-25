from django.urls import path
from .views import (
    SubscriptionStatusView,
    StripeCreateCheckoutView,
    StripeWebhookView,
    StripeCancelView,
    RevenueCatWebhookView,
    # Legacy views for backward compatibility
    UpgradeView,
    CancelView,
    ValidateStripeView,
    ValidateAppleView,
)

urlpatterns = [
    # Shared
    path('status/', SubscriptionStatusView.as_view(), name='subscription_status'),

    # Android — Stripe
    path('stripe/create-checkout/', StripeCreateCheckoutView.as_view(), name='stripe_checkout'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('stripe/cancel/', StripeCancelView.as_view(), name='stripe_cancel'),

    # iOS — RevenueCat/Apple IAP
    path('revenuecat/webhook/', RevenueCatWebhookView.as_view(), name='revenuecat_webhook'),

    # Legacy (for backward compatibility / testing)
    path('upgrade/', UpgradeView.as_view(), name='subscription_upgrade'),
    path('cancel/', CancelView.as_view(), name='subscription_cancel'),
    path('validate-stripe/', ValidateStripeView.as_view(), name='validate_stripe'),
    path('validate-apple/', ValidateAppleView.as_view(), name='validate_apple'),
]
