from django.db import models
from django.conf import settings

class InterviewSession(models.Model):
    TYPE_CHOICES = (
        ('SCRIPTED', 'Scripted'),
        ('AI', 'AI'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('FINISHED', 'Finished'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    score = models.IntegerField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} ({self.status})"

class InterviewMessage(models.Model):
    ROLE_CHOICES = (
        ('USER', 'User'),
        ('BOT', 'Bot'),
    )
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.text[:50]}"
