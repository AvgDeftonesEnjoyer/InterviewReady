from django.contrib import admin
from .models import InterviewSession, InterviewMessage

class InterviewMessageInline(admin.TabularInline):
    model = InterviewMessage
    extra = 0
    readonly_fields = ('role', 'text', 'created_at')
    can_delete = False

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'status', 'score', 'started_at', 'finished_at')
    list_filter = ('type', 'status')
    search_fields = ('user__username', 'user__email')
    inlines = [InterviewMessageInline]
