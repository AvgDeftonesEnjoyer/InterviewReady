from django.db import models
from django.conf import settings


class InterviewSession(models.Model):
    MODE_CHOICES = [
        ('hr', 'HR Only'),
        ('tech', 'Technical Only'),
        ('combined', 'HR + Technical'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions'
    )
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    language = models.CharField(max_length=50, blank=True, default='')
    question_count_target = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    messages = models.JSONField(default=list)
    question_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.mode} ({self.status})"
