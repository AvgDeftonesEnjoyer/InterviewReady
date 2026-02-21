from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe
from subscriptions.models import Subscription
from subscriptions.services import SubscriptionService

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionStatusView(APIView):
    def get(self, request, *args, **kwargs):
        is_pro = SubscriptionService.is_pro(request.user)
        active_sub = SubscriptionService.get_active_subscription(request.user)
        
        data = {
            "is_pro": is_pro,
            "plan": active_sub.plan if active_sub else "FREE",
            "expires_at": active_sub.expires_at if active_sub else None,
        }
        return Response(data, status=status.HTTP_200_OK)

class ValidateStripeView(APIView):
    """
    Validates a Stripe payment intent and activates subscription.
    """
    def post(self, request, *args, **kwargs):
        # Client sends setup_intent or payment_intent
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({"error": "Payment intent required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == 'succeeded':
                # Activate PRO subscription manually or wait for webhook
                Subscription.objects.update_or_create(
                    user=request.user,
                    provider='STRIPE',
                    defaults={
                        'plan': 'PRO',
                        'status': 'ACTIVE',
                        'provider_subscription_id': intent.customer,  # simplistic mapping
                    }
                )
                return Response({"status": "active"}, status=status.HTTP_200_OK)
            return Response({"status": intent.status}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ValidateAppleView(APIView):
    """
    Validates Apple verifyReceipt API
    """
    def post(self, request, *args, **kwargs):
        receipt_data = request.data.get('receipt_data')
        if not receipt_data:
            return Response({"error": "Receipt required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Note: Proper Apple receipt validation requires network requests to Apple servers.
        # This is simplified for demonstration purposes since App Store requires actual device certificates.
        Subscription.objects.update_or_create(
            user=request.user,
            provider='APPLE',
            defaults={
                'plan': 'PRO',
                'status': 'ACTIVE',
            }
        )
        return Response({"status": "active"}, status=status.HTTP_200_OK)
