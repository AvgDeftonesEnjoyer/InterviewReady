from django.db import models
from django.conf import settings
from django.utils import timezone

class AIUsage(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_usage')
    used_today = models.IntegerField(default=0)
    daily_limit = models.IntegerField(default=5)
    last_reset = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.used_today}/{self.daily_limit} used"
