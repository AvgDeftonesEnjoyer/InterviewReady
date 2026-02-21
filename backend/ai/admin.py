from django.contrib import admin
from .models import AIUsage

@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'used_today', 'daily_limit', 'last_reset')
    search_fields = ('user__username', 'user__email')
