from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    PRIMARY_LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('go', 'Go'),
        ('csharp', 'C#'),
    ]
    primary_language = models.CharField(max_length=50, choices=PRIMARY_LANGUAGE_CHOICES, blank=True, null=True)
    
    SPECIALIZATION_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('fullstack', 'Fullstack'),
        ('data', 'Data Science'),
        ('ml', 'ML/AI'),
    ]
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, blank=True, null=True)
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
    ]
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    
    onboarding_completed = models.BooleanField(default=False)
    
    ui_language = models.CharField(
        max_length=5,
        choices=[('en', 'English'), ('uk', 'Українська')],
        default='en'
    )
    
    # Existing fields
    target_role = models.CharField(max_length=100, blank=True, null=True)
    readiness_score = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}'s Profile - Level {self.current_level}"

class Streak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True)

class ChallengeTemplate(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    
    challenge_type = models.CharField(max_length=50, choices=[
        ('answer_questions', 'Answer N Questions'),
        ('answer_hard',      'Answer N Hard Questions'),
        ('complete_topic',   'Complete a Topic'),
        ('ai_interview',     'Do AI Interview Session'),
        ('streak_protect',   'Answer at least 1 question'),
        ('perfect_score',    'Get 100% on N questions'),
    ])
    
    language = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=20, blank=True)
    
    goal_count = models.IntegerField()
    bonus_xp = models.IntegerField(default=100)
    icon = models.CharField(max_length=10, default='🏆')
    
    is_active = models.BooleanField(default=True)
    
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy',   'Easy'),
        ('medium', 'Medium'),
        ('hard',   'Hard'),
    ], default='easy')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Challenge Template'
        verbose_name_plural = 'Challenge Templates'

    def __str__(self):
        return f"{self.icon} {self.title}"

class DailyChallenge(models.Model):
    template = models.ForeignKey(
        ChallengeTemplate, 
        on_delete=models.SET_NULL, 
        null=True
    )
    date = models.DateField()
    order = models.IntegerField(default=1)

    class Meta:
        unique_together = ('date', 'order')
        ordering = ['date', 'order']
        
    def __str__(self):
        return f"{self.date} - {self.template.title if self.template else 'Deleted Template'}"

class UserDailyChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_challenges')
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    
    completed_count = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    xp_awarded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'challenge')
