from django.contrib import admin
from .models import Question, AnswerOption, UserAnswer, UserProgress

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'difficulty', 'language', 'is_active', 'xp_reward')
    list_filter = ('difficulty', 'language', 'specialization', 'is_active')
    inlines = [AnswerOptionInline]

admin.site.register(UserAnswer)
admin.site.register(UserProgress)
