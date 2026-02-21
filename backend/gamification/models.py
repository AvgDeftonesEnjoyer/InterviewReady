from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    target_role = models.CharField(max_length=100, blank=True, null=True)
    experience_level = models.CharField(max_length=50, blank=True, null=True)
    readiness_score = models.IntegerField(default=0)
    
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    
    streak_days = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - Level {self.current_level}"
