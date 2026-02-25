from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model for InterviewReady.
    Email is unique, username can be any value.
    Authentication is done via email.
    """
    is_internal_tester = models.BooleanField(
        default=False,
        help_text="Designates whether the user bypasses subscription checks."
    )
    
    # Make email unique
    email = models.EmailField(unique=True)
    
    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Required when creating superuser

    def __str__(self):
        return self.email

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
