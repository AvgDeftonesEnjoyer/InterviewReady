from django.db import models
from django.conf import settings

class Question(models.Model):
    DIFFICULTY_CHOICES = (
        ('JUNIOR', 'Junior'),
        ('MIDDLE', 'Middle'),
        ('SENIOR', 'Senior'),
    )
    LANGUAGE_CHOICES = (
        ('EN', 'English'),
        ('UA', 'Ukrainian'),
    )

    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='EN')
    text = models.TextField()
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.text[:50]}"

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option for {self.question.id}: {self.text[:30]}"

class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.id} (Correct: {self.is_correct})"
