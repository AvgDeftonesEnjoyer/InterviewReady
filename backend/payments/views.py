import json
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from subscriptions.models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        data = event['data']['object']
        
        if event['type'] == 'customer.subscription.created' or event['type'] == 'customer.subscription.updated':
            # Handle activation / updates
            customer_id = data.get('customer')
            status = data.get('status')
            if status == 'active':
                Subscription.objects.filter(provider_subscription_id=customer_id).update(status='ACTIVE')
        elif event['type'] == 'customer.subscription.deleted':
            customer_id = data.get('customer')
            Subscription.objects.filter(provider_subscription_id=customer_id).update(status='CANCELED')
        
        return HttpResponse(status=200)

class AppleWebhookView(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        # Apple Sever Notification webhook handling
        payload = json.loads(request.body)
        notification_type = payload.get('notification_type')

        # Apple's payload structure is complex. E.g: DID_RENEW, CANCEL, DID_FAIL_TO_RENEW
        original_transaction_id = payload.get('original_transaction_id') # simplistic extraction
        
        if not original_transaction_id:
            return HttpResponse(status=400)

        if notification_type in ['DID_RENEW', 'SUBSCRIBED']:
            Subscription.objects.filter(provider_subscription_id=original_transaction_id).update(status='ACTIVE')
        elif notification_type in ['CANCEL', 'EXPIRED', 'DID_FAIL_TO_RENEW']:
            Subscription.objects.filter(provider_subscription_id=original_transaction_id).update(status='EXPIRED')
            
        return HttpResponse(status=200)
