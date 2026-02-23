from django.urls import path
from .views import SubscriptionStatusView, UpgradeView, CancelView, ValidateStripeView, ValidateAppleView

urlpatterns = [
    path('status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('upgrade/', UpgradeView.as_view(), name='subscription_upgrade'),
    path('cancel/', CancelView.as_view(), name='subscription_cancel'),
    
    # Internal validation/providers
    path('validate-stripe/', ValidateStripeView.as_view(), name='validate_stripe'),
    path('validate-apple/', ValidateAppleView.as_view(), name='validate_apple'),
]
