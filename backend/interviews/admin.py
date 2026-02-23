from django.contrib import admin
from .models import InterviewSession


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode', 'status', 'question_count', 'started_at', 'finished_at')
    list_filter = ('mode', 'status')
    search_fields = ('user__username', 'user__email')
