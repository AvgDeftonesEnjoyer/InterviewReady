from django.db import models
from django.conf import settings


class InterviewSession(models.Model):
    class Mode(models.TextChoices):
        HR = 'hr', 'HR Only'
        TECH = 'tech', 'Technical Only'
        COMBINED = 'combined', 'HR + Technical'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions'
    )
    mode = models.CharField(max_length=20, choices=Mode.choices)
    language = models.CharField(max_length=50, blank=True, default='')
    question_count_target = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    messages = models.JSONField(default=list)
    question_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        # OPTIMIZATION: Add indexes for frequently filtered fields
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['user', 'mode']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.mode} ({self.status})"
