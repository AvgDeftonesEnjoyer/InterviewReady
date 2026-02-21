from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model for InterviewReady.
    """
    is_internal_tester = models.BooleanField(
        default=False,
        help_text="Designates whether the user bypasses subscription checks."
    )

    def __str__(self):
        return self.username

class SocialAccount(models.Model):
    PROVIDER_CHOICES = (
        ('GOOGLE', 'Google'),
        ('APPLE', 'Apple'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'provider_user_id')

    def __str__(self):
        return f"{self.user.username} - {self.provider}"
