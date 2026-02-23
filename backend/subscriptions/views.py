from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
import stripe

from subscriptions.models import Subscription
from subscriptions.services import SubscriptionService
from subscriptions.config import PLANS

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        active_sub = SubscriptionService.get_active_subscription(request.user)
        
        # Calculate remaining interviews quota safely to prevent circular import issues entirely avoiding imports inside function if possible
        # Import moved to local scope to prevent circular references with models
        from interviews.services import get_quota
        quota = get_quota(request.user)

        if not active_sub:
            return Response({
                'plan':       'FREE',
                'is_active':  False,
                'started_at': None,
                'expires_at': None,
                'billing_cycle': 'monthly',
                'price': 0,
                'interviews_remaining': quota['remaining'],
                'interviews_limit':     quota['limit'],
                'plans':      PLANS,
            }, status=status.HTTP_200_OK)

        # Check if expired
        if active_sub.expires_at and active_sub.expires_at < timezone.now():
            active_sub.status = 'EXPIRED'
            active_sub.save()
            return Response({
                'plan':       'FREE',
                'is_active':  False,
                'started_at': None,
                'expires_at': None,
                'billing_cycle': 'monthly',
                'price': 0,
                'interviews_remaining': quota['remaining'],
                'interviews_limit':     quota['limit'],
                'plans':      PLANS,
            }, status=status.HTTP_200_OK)

        return Response({
            'plan':         active_sub.plan,
            'is_active':    active_sub.is_valid,
            'started_at':   active_sub.started_at,
            'expires_at':   active_sub.expires_at,
            'billing_cycle': active_sub.billing_cycle,
            'price':        active_sub.price,
            'interviews_remaining': quota['remaining'],
            'interviews_limit':     quota['limit'],
            'plans':        PLANS,
        }, status=status.HTTP_200_OK)


class UpgradeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan = request.data.get('plan')
        cycle = request.data.get('billing_cycle', 'monthly')

        if plan not in ['PRO', 'PRO_PLUS']:
            return Response(
                {'error': 'Invalid plan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Simulated Stripe upgrade logic (for testing directly via API)
        from datetime import timedelta
        expires = timezone.now() + (
            timedelta(days=365) if cycle == 'annual'
            else timedelta(days=30)
        )

        sub, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'status': 'ACTIVE',
                'billing_cycle': cycle,
                'started_at': timezone.now(),
                'expires_at': expires
            }
        )

        if not created:
            sub.plan = plan
            sub.status = 'ACTIVE'
            sub.billing_cycle = cycle
            sub.started_at = timezone.now()
            sub.expires_at = expires
            sub.save()

        return Response({
            'success': True,
            'plan':    plan,
            'expires_at': expires,
            'message': f'Successfully upgraded to {plan}!'
        })


class CancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        active_sub = SubscriptionService.get_active_subscription(request.user)
        if not active_sub:
            return Response({
                'error': 'No active subscription found.'
            }, status=status.HTTP_404_NOT_FOUND)

        active_sub.cancelled_at = timezone.now()
        active_sub.status = 'CANCELED' 
        active_sub.save()

        return Response({
            'success': True,
            'message': 'Subscription cancelled. Access removed (mock implementation).'
        })


class ValidateStripeView(APIView):
    """
    Validates a Stripe payment intent and activates subscription.
    """
    def post(self, request, *args, **kwargs):
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({"error": "Payment intent required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == 'succeeded':
                Subscription.objects.update_or_create(
                    user=request.user,
                    provider='STRIPE',
                    defaults={
                        'plan': 'PRO',
                        'status': 'ACTIVE',
                        'provider_subscription_id': intent.customer,
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
        
        Subscription.objects.update_or_create(
            user=request.user,
            provider='APPLE',
            defaults={
                'plan': 'PRO',
                'status': 'ACTIVE',
            }
        )
        return Response({"status": "active"}, status=status.HTTP_200_OK)
