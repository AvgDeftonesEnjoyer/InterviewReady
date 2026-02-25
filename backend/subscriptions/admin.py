from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'plan', 'status', 'payment_provider', 'is_valid',
        'billing_cycle', 'started_at', 'expires_at',
        'stripe_customer_id', 'stripe_subscription_id'
    )
    list_filter = ('plan', 'status', 'payment_provider', 'billing_cycle')
    list_editable = ('plan', 'status', 'billing_cycle')
    search_fields = ('user__username', 'user__email', 'provider_subscription_id', 'stripe_subscription_id')
    readonly_fields = (
        'stripe_customer_id',
        'stripe_subscription_id',
        'revenuecat_user_id',
    )

    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
