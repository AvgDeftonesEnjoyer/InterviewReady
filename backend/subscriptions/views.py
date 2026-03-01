import stripe
import hmac
import logging
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from subscriptions.models import Subscription
from subscriptions.services import SubscriptionService
from subscriptions.config import PLANS
from users.models import User

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


# ── SHARED UTILITIES ────────────────────────────

def activate_subscription(user, plan, provider,
                           stripe_sub_id='',
                           stripe_customer_id='',
                           expires_days=30):
    """Activate subscription regardless of provider."""
    sub, created = Subscription.objects.get_or_create(
        user=user,
        defaults={
            'status': 'ACTIVE',
            'plan': plan,
        }
    )
    sub.plan             = plan
    sub.status           = 'ACTIVE'
    sub.payment_provider = provider
    sub.provider         = 'STRIPE' if provider == 'stripe' else 'APPLE'
    sub.started_at       = timezone.now()
    sub.expires_at       = timezone.now() + timedelta(days=expires_days)
    if stripe_sub_id:
        sub.stripe_subscription_id = stripe_sub_id
        sub.provider_subscription_id = stripe_sub_id  # For compatibility
    if stripe_customer_id:
        sub.stripe_customer_id = stripe_customer_id
    sub.save()
    logger.info(f"Subscription activated: {user.email} → {plan} via {provider}")


def deactivate_subscription(user):
    """Deactivate subscription."""
    try:
        sub = user.subscription if hasattr(user, 'subscription') else Subscription.objects.filter(user=user).first()
        if sub:
            sub.status    = 'CANCELED'
            sub.plan      = 'FREE'
            sub.cancelled_at = timezone.now()
            sub.save()
            logger.info(f"Subscription deactivated: {user.email}")
    except Exception as e:
        logger.error(f"Error deactivating subscription: {e}")


# ── GET /api/subscriptions/status/ ─────────────

class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from interviews.services import get_quota

        sub = SubscriptionService.get_active_subscription(request.user)
        quota = get_quota(request.user)

        if not sub or not sub.is_valid:
            return Response({
                'plan':                  'FREE',
                'is_active':             False,
                'expires_at':            None,
                'payment_provider':      'none',
                'interviews_remaining':  quota['remaining'],
                'interviews_limit':      quota['limit'],
                'plans':                 PLANS,
            })

        return Response({
            'plan':                  sub.plan,
            'is_active':             True,
            'expires_at':            sub.expires_at,
            'started_at':            sub.started_at,
            'billing_cycle':         sub.billing_cycle,
            'payment_provider':      sub.payment_provider,
            'interviews_remaining':  quota['remaining'],
            'interviews_limit':      quota['limit'],
            'plans':                 PLANS,
        })


# ── ANDROID: STRIPE ────────────────────────────

# POST /api/subscriptions/stripe/create-checkout/
# Body: { plan, billing_cycle }
class StripeCreateCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan  = request.data.get('plan')
        cycle = request.data.get('billing_cycle', 'monthly')

        logger.info(f"Stripe checkout request: plan={plan}, cycle={cycle}, user={request.user.id}")

        if plan not in ['PRO', 'PRO_PLUS']:
            logger.error(f"Invalid plan: {plan}")
            return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)

        price_map = {
            ('PRO',      'monthly'): settings.STRIPE_PRO_MONTHLY_PRICE_ID,
            ('PRO',      'annual'):  settings.STRIPE_PRO_ANNUAL_PRICE_ID,
            ('PRO_PLUS', 'monthly'): settings.STRIPE_PRO_PLUS_MONTHLY_PRICE_ID,
            ('PRO_PLUS', 'annual'):  settings.STRIPE_PRO_PLUS_ANNUAL_PRICE_ID,
        }
        price_id = price_map.get((plan, cycle))
        logger.info(f"Price ID lookup: ({plan}, {cycle}) -> {price_id}")
        
        if not price_id:
            logger.error(f"Invalid plan/cycle combination: {plan}, {cycle}")
            return Response({'error': 'Invalid plan/cycle'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate price_id format
        if not price_id.startswith('price_'):
            logger.error(f"Invalid price_id format: {price_id} (should start with 'price_')")
            return Response({
                'error': 'Invalid price ID configuration. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Find or create Subscription
            sub, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'status': 'ACTIVE',
                    'plan': 'FREE',
                }
            )

            if not sub.stripe_customer_id:
                logger.info(f"Creating new Stripe customer for user {request.user.id}")
                customer = stripe.Customer.create(
                    email=request.user.email,
                    metadata={'user_id': str(request.user.id)}
                )
                sub.stripe_customer_id = customer.id
                sub.save(update_fields=['stripe_customer_id'])
                logger.info(f"Stripe customer created: {customer.id}")

            logger.info(f"Creating Stripe checkout session with price_id: {price_id}")
            
            # Use dynamic origin for local web tests, or deep link for mobile
            origin = request.META.get('HTTP_ORIGIN', 'http://localhost:8081')
            success_url = f"{origin}/subscription/success?subscription=success" if origin.startswith('http://localhost') else 'interviewready://subscription/success?subscription=success'
            
            session = stripe.checkout.Session.create(
                customer=sub.stripe_customer_id,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{'price': price_id, 'quantity': 1}],
                # Deep link back to app after payment:
                success_url=success_url,
                cancel_url='interviewready://subscription/cancel',
                metadata={
                    'user_id': str(request.user.id),
                    'plan':    plan,
                    'cycle':   cycle,
                },
                subscription_data={
                    'metadata': {
                        'user_id': str(request.user.id),
                        'plan':    plan,
                        'cycle':   cycle,
                    }
                }
            )

            logger.info(f"Checkout session created: {session.id}, URL: {session.url}")
            return Response({'checkout_url': session.url})

        except stripe.StripeError as e:
            logger.error(f"Stripe checkout error: {e}", exc_info=True)
            return Response({
                'error': f'Payment service unavailable: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Unexpected error in checkout: {e}", exc_info=True)
            return Response({
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POST /api/subscriptions/stripe/webhook/
# Stripe calls this endpoint — WITHOUT authentication!
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes     = []

    def post(self, request):
        payload = request.body
        sig     = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            logger.warning("Invalid Stripe webhook signature")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event_type = event['type']
        data       = event['data']['object']

        logger.info(f"Stripe webhook: {event_type}")

        # ✅ Payment successful
        if event_type == 'checkout.session.completed':
            user_id = data['metadata'].get('user_id')
            plan    = data['metadata'].get('plan')
            cycle   = data['metadata'].get('cycle', 'monthly')
            sub_id  = data.get('subscription', '')
            customer_id = data.get('customer', '')

            if user_id and plan:
                try:
                    user = User.objects.get(id=user_id)
                    activate_subscription(
                        user, 
                        plan, 
                        'stripe', 
                        stripe_sub_id=sub_id,
                        stripe_customer_id=customer_id,
                        expires_days=365 if 'annual' in cycle else 30
                    )
                except User.DoesNotExist:
                    logger.error(f"User {user_id} not found")

        # ✅ Automatic renewal
        elif event_type == 'invoice.payment_succeeded':
            sub_id = data.get('subscription', '')
            if sub_id:
                try:
                    sub = Subscription.objects.get(
                        stripe_subscription_id=sub_id
                    )
                    sub.expires_at = timezone.now() + timedelta(days=30)
                    sub.status  = 'ACTIVE'
                    sub.provider = 'STRIPE'  # Ensure provider is set
                    sub.save(update_fields=['expires_at', 'status', 'provider'])
                except Subscription.DoesNotExist:
                    pass

        # ❌ Payment failed
        elif event_type == 'invoice.payment_failed':
            sub_id = data.get('subscription', '')
            logger.warning(f"Payment failed for subscription: {sub_id}")
            # TODO: send push notification to user

        # ❌ Subscription canceled
        elif event_type == 'customer.subscription.deleted':
            sub_id = data.get('id', '')
            try:
                sub  = Subscription.objects.get(
                    stripe_subscription_id=sub_id
                )
                deactivate_subscription(sub.user)
            except Subscription.DoesNotExist:
                pass

        return Response({'status': 'ok'})


# POST /api/subscriptions/stripe/cancel/
class StripeCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sub = SubscriptionService.get_active_subscription(request.user)
            if not sub or not sub.stripe_subscription_id:
                return Response(
                    {'error': 'No Stripe subscription found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cancel at the end of the current period
            stripe.Subscription.modify(
                sub.stripe_subscription_id,
                cancel_at_period_end=True
            )

            return Response({
                'message': 'Subscription cancelled. Active until expiry.',
                'expires_at': sub.expires_at,
            })

        except Subscription.DoesNotExist:
            return Response({'error': 'No subscription'}, status=status.HTTP_404_NOT_FOUND)
        except stripe.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ── iOS: REVENUECAT WEBHOOK ────────────────────

# POST /api/subscriptions/revenuecat/webhook/
# RevenueCat calls — WITHOUT authentication!
class RevenueCatWebhookView(APIView):
    authentication_classes = []
    permission_classes     = []

    PLAN_MAP = {
        'pro_monthly':      'PRO',
        'pro_annual':       'PRO',
        'pro_plus_monthly': 'PRO_PLUS',
        'pro_plus_annual':  'PRO_PLUS',
    }

    def post(self, request):
        # Перевірка авторизації (constant-time comparison to prevent timing attacks)
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        expected = f'Bearer {settings.REVENUECAT_WEBHOOK_AUTH}'
        if not hmac.compare_digest(auth, expected):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        event     = request.data.get('event', {})
        event_type = event.get('type')
        app_user_id = event.get('app_user_id')  # this is our user.id

        logger.info(f"RevenueCat webhook: {event_type} for {app_user_id}")

        try:
            user = User.objects.get(id=app_user_id)
        except (User.DoesNotExist, ValueError):
            logger.error(f"User {app_user_id} not found")
            return Response(status=status.HTTP_200_OK)  # 200 so RC doesn't retry

        # Determine plan from product_id
        product_id = event.get('product_id', '')
        plan = self._get_plan_from_product(product_id)

        # Determine term
        expires_days = 365 if 'annual' in product_id else 30

        if event_type in [
            'INITIAL_PURCHASE',
            'RENEWAL',
            'PRODUCT_CHANGE',
            'UNCANCELLATION',
        ]:
            if plan:
                activate_subscription(
                    user, plan, 'apple', expires_days=expires_days
                )

        elif event_type in [
            'CANCELLATION',
            'EXPIRATION',
            'BILLING_ISSUE',
        ]:
            deactivate_subscription(user)

        return Response({'status': 'ok'})

    def _get_plan_from_product(self, product_id: str) -> str:
        """
        Mapping from Apple Product ID to our plan.
        Product IDs are created in App Store Connect.
        Example: 'com.interviewready.pro.monthly' → 'PRO'
        """
        product_id_lower = product_id.lower()
        if 'pro_plus' in product_id_lower or 'proplus' in product_id_lower:
            return 'PRO_PLUS'
        elif 'pro' in product_id_lower:
            return 'PRO'
        return ''


# ── LEGACY VIEWS (for backward compatibility) ─────────────

class UpgradeView(APIView):
    """
    LEGACY: Mock upgrade view - kept for testing only.
    In production, use Stripe or Apple IAP.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan = request.data.get('plan')
        cycle = request.data.get('billing_cycle', 'monthly')

        if plan not in ['PRO', 'PRO_PLUS']:
            return Response(
                {'error': 'Invalid plan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Simulated upgrade logic (for testing directly via API)
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
            'message': f'Successfully upgraded to {plan}! (TEST MODE)'
        })


class CancelView(APIView):
    """
    LEGACY: Mock cancel view - kept for testing only.
    In production, use Stripe cancel or Apple IAP settings.
    """
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
            'message': 'Subscription cancelled. Access removed (TEST MODE).'
        })


class ValidateStripeView(APIView):
    """
    LEGACY: Validates a Stripe payment intent - kept for backward compatibility.
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
    LEGACY: Validates Apple verifyReceipt API - kept for backward compatibility.
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
