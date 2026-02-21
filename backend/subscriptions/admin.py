from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'provider', 'status', 'started_at', 'expires_at')
    list_filter = ('plan', 'provider', 'status')
    search_fields = ('user__username', 'user__email', 'provider_subscription_id')
