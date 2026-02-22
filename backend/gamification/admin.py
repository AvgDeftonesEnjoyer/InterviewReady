from django.contrib import admin
from .models import UserProfile, Streak, ChallengeTemplate, DailyChallenge, UserDailyChallenge

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_language', 'specialization', 'experience_level', 'current_level', 'total_xp')
    search_fields = ('user__username', 'user__email')

@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'last_activity_date')

@admin.register(ChallengeTemplate)
class ChallengeTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'icon', 'title', 'challenge_type', 
        'language', 'difficulty', 'goal_count', 
        'bonus_xp', 'difficulty_level', 'is_active'
    ]
    list_filter = [
        'challenge_type', 'language', 
        'difficulty_level', 'is_active'
    ]
    list_editable = ['is_active', 'bonus_xp']
    search_fields = ['title', 'description']

@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ['date', 'order', 'template']
    list_filter = ['date']

@admin.register(UserDailyChallenge)
class UserDailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'is_completed', 'completed_count')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'challenge__template__title')
