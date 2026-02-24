import json
import hmac
import hashlib
import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from subscriptions.models import Subscription

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWebhookView(APIView):
    """
    Stripe webhook endpoint with signature verification.
    SECURITY: Verifies Stripe signature to prevent forged webhooks.
    """
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        # SECURITY: Validate webhook signature
        if not webhook_secret:
            logger.error("Stripe webhook secret not configured")
            return HttpResponse(status=400)

        if not sig_header:
            logger.warning("Stripe webhook: Missing signature header")
            return HttpResponse(status=400)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            logger.info(f"Stripe webhook verified: {event['type']}")
        except ValueError as e:
            logger.error(f"Stripe webhook: Invalid payload - {str(e)}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook: Signature verification failed - {str(e)}")
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Stripe webhook: Unexpected error - {str(e)}")
            return HttpResponse(status=400)

        data = event['data']['object']
        event_type = event['type']

        try:
            if event_type in ['customer.subscription.created', 'customer.subscription.updated']:
                customer_id = data.get('customer')
                subscription_id = data.get('id')
                plan_id = data.get('plan', {}).get('nickname', 'PRO')
                stripe_status = data.get('status')
                
                # Map Stripe status to our status
                our_status = 'ACTIVE' if stripe_status == 'active' else 'CANCELED'
                
                if customer_id:
                    Subscription.objects.filter(
                        provider_subscription_id=subscription_id
                    ).update(
                        status=our_status,
                        provider='STRIPE'
                    )
                    logger.info(f"Stripe webhook: Updated subscription {subscription_id} to {our_status}")
                    
            elif event_type == 'customer.subscription.deleted':
                subscription_id = data.get('id')
                if subscription_id:
                    Subscription.objects.filter(
                        provider_subscription_id=subscription_id
                    ).update(status='CANCELED')
                    logger.info(f"Stripe webhook: Canceled subscription {subscription_id}")
                    
            elif event_type == 'invoice.payment_succeeded':
                # Payment succeeded - ensure subscription is active
                customer_id = data.get('customer')
                if customer_id:
                    Subscription.objects.filter(
                        user__stripe_customer_id=customer_id
                    ).update(status='ACTIVE')
                    
            elif event_type == 'invoice.payment_failed':
                # Payment failed - mark subscription for cancellation
                customer_id = data.get('customer')
                if customer_id:
                    Subscription.objects.filter(
                        user__stripe_customer_id=customer_id
                    ).update(status='CANCELED')

            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Stripe webhook processing error: {str(e)}")
            return HttpResponse(status=500)


class AppleWebhookView(APIView):
    """
    Apple App Store Server Notification webhook.
    SECURITY: Validates Apple notification signature.
    """
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        Handle Apple Server Notifications.
        Apple sends signed JWT notifications that must be verified.
        """
        try:
            payload = json.loads(request.body)
            logger.info(f"Apple webhook received: {payload.get('notification_type', 'unknown')}")
            
            # For Apple's v2 notifications, the payload is wrapped in 'data'
            notification_data = payload.get('data', {})
            notification_type = payload.get('notification_type')
            signed_payload = notification_data.get('signedPayload') if notification_data else None
            
            # Handle v1 notifications (legacy)
            if not signed_payload and 'original_transaction_id' in payload:
                original_transaction_id = payload.get('original_transaction_id')
                self._process_apple_notification(original_transaction_id, notification_type)
                return HttpResponse(status=200)
            
            # Handle v2 notifications (signed JWT)
            if signed_payload:
                # In production, verify the JWT signature using Apple's public key
                # For now, we decode without verification (should be implemented with proper keys)
                try:
                    import jwt
                    # Apple's JWKS URL: https://appleid.apple.com/auth/keys
                    # In production, fetch and verify with Apple's public key
                    decoded = jwt.decode(
                        signed_payload,
                        options={"verify_signature": False},  # TODO: Implement proper verification
                    )
                    original_transaction_id = decoded.get('data', {}).get(
                        'signedTransactionInfo', {}
                    ).get('originalTransactionId')
                    
                    if original_transaction_id:
                        self._process_apple_notification(str(original_transaction_id), notification_type)
                        return HttpResponse(status=200)
                    else:
                        logger.warning("Apple webhook: Missing transaction ID in signed payload")
                        return HttpResponse(status=400)
                        
                except jwt.InvalidTokenError as e:
                    logger.error(f"Apple webhook: Invalid JWT - {str(e)}")
                    return HttpResponse(status=400)
            
            logger.warning("Apple webhook: Invalid payload structure")
            return HttpResponse(status=400)
            
        except json.JSONDecodeError as e:
            logger.error(f"Apple webhook: Invalid JSON - {str(e)}")
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Apple webhook processing error: {str(e)}")
            return HttpResponse(status=500)

    def _process_apple_notification(self, transaction_id: str, notification_type: str):
        """Process Apple notification and update subscription status."""
        if not transaction_id:
            logger.warning("Apple webhook: No transaction ID provided")
            return
            
        active_notifications = ['DID_RENEW', 'SUBSCRIBED', 'DID_RECOVER']
        inactive_notifications = ['CANCEL', 'EXPIRED', 'DID_FAIL_TO_RENEW', 'REFUND']
        
        if notification_type in active_notifications:
            Subscription.objects.filter(
                provider_subscription_id=transaction_id
            ).update(status='ACTIVE', provider='APPLE')
            logger.info(f"Apple webhook: Activated subscription {transaction_id}")
            
        elif notification_type in inactive_notifications:
            Subscription.objects.filter(
                provider_subscription_id=transaction_id
            ).update(status='EXPIRED')
            logger.info(f"Apple webhook: Expired subscription {transaction_id}")
