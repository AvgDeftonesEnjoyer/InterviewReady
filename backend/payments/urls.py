from django.urls import path
from .views import StripeWebhookView, AppleWebhookView

urlpatterns = [
    path('stripe/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('apple/', AppleWebhookView.as_view(), name='apple_webhook'),
]
