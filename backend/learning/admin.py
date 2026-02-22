from django.contrib import admin
from .models import Topic, Question, AnswerOption, UserAnswer, UserProgress

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4
    fields = ['text_en', 'text_uk', 'is_correct', 'order']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'language', 'specialization', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['language', 'specialization']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_en', 'topic', 'difficulty', 'question_type', 'xp_reward']
    list_filter = ['topic', 'difficulty', 'question_type', 'language']
    inlines = [AnswerOptionInline]
    
    fieldsets = [
        ('English', {
            'fields': ['text_en', 'explanation_en']
        }),
        ('Українська', {
            'fields': ['text_uk', 'explanation_uk']
        }),
        ('Settings', {
            'fields': ['topic', 'language', 'specialization', 'difficulty',
                      'question_type', 'xp_reward', 'is_active']
        }),
    ]

admin.site.register(UserAnswer)
admin.site.register(UserProgress)
