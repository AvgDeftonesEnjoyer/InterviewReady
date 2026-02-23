from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'plan', 'status', 'provider', 'is_valid',
        'billing_cycle', 'started_at', 'expires_at'
    )
    list_filter = ('plan', 'status', 'provider', 'billing_cycle')
    list_editable = ('plan', 'status', 'billing_cycle')
    search_fields = ('user__username', 'user__email', 'provider_subscription_id')
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
