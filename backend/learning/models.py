from django.db import models
from django.conf import settings

class Topic(models.Model):
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    specialization = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=10, default='📚')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    name_en = models.CharField(max_length=100, blank=True)
    name_uk = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['order']

    def get_name(self, lang='en'):
        if lang == 'uk' and self.name_uk:
            return self.name_uk
        return self.name_en or self.name

    def __str__(self):
        return f"{self.icon} {self.name} ({self.language})"


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

    QUESTION_TYPE_CHOICES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True / False'),
        ('text', 'Short Text'),
    )

    text = models.TextField()
    language = models.CharField(max_length=50, choices=PROGRAMMING_LANGUAGE_CHOICES, default='python')
    specialization = models.CharField(max_length=50, default='backend', blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name='questions')
    xp_reward = models.IntegerField(default=10)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    text_en = models.TextField(default='', blank=True)
    text_uk = models.TextField(blank=True)
    explanation_en = models.TextField(blank=True)
    explanation_uk = models.TextField(blank=True)

    def get_text(self, lang='en'):
        if lang == 'uk' and self.text_uk:
            return self.text_uk
        return self.text_en or self.text

    def get_explanation(self, lang='en'):
        if lang == 'uk' and self.explanation_uk:
            return self.explanation_uk
        return self.explanation_en or self.explanation

    def __str__(self):
        topic_name = self.topic.name if self.topic else "No Topic"
        return f"[{self.language} - {topic_name}] {self.text[:50]}"

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    text_en = models.CharField(max_length=500, default='', blank=True)
    text_uk = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['order']

    def get_text(self, lang='en'):
        if lang == 'uk' and self.text_uk:
            return self.text_uk
        return self.text_en or self.text

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
    session_id = models.CharField(max_length=100, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField()
    xp_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Progress on Q{self.question.id} (XP: {self.xp_earned})"
