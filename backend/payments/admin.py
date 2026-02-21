from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_id', 'provider', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('provider', 'status')
    search_fields = ('user__username', 'user__email', 'transaction_id')
