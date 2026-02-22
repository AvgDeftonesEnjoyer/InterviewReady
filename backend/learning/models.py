from django.db import models
from django.conf import settings

class Question(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    PROGRAMMING_LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('go', 'Go'),
        ('csharp', 'C#'),
    ]

    text = models.TextField()
    language = models.CharField(max_length=50, choices=PROGRAMMING_LANGUAGE_CHOICES, default='python')
    specialization = models.CharField(max_length=50, default='backend')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    topic = models.CharField(max_length=100, default='General')
    xp_reward = models.IntegerField(default=10)
    
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.language} - {self.topic}] {self.text[:50]}"

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

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField()
    xp_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Progress on Q{self.question.id} (XP: {self.xp_earned})"
