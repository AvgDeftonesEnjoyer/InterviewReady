from django.db import models
from django.conf import settings
from django.utils import timezone

class AIUsage(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_usage')
    used_today = models.IntegerField(default=0)
    daily_limit = models.IntegerField(default=5)
    last_reset = models.DateField(default=timezone.now)

    class Meta:
        # OPTIMIZATION: Add indexes for frequently filtered fields
        indexes = [
            models.Index(fields=['user', 'last_reset']),
            models.Index(fields=['last_reset']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.used_today}/{self.daily_limit} used"
