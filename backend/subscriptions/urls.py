from django.urls import path
from .views import SubscriptionStatusView, ValidateStripeView, ValidateAppleView

urlpatterns = [
    path('', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('validate-stripe/', ValidateStripeView.as_view(), name='validate_stripe'),
    path('validate-apple/', ValidateAppleView.as_view(), name='validate_apple'),
]
