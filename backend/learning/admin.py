from django.contrib import admin
from .models import Question, AnswerOption, UserAnswer

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'difficulty', 'language', 'is_active')
    list_filter = ('difficulty', 'category', 'language', 'is_active')
    inlines = [AnswerOptionInline]

admin.site.register(UserAnswer)
