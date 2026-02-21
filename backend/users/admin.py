from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SocialAccount

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('is_internal_tester',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(SocialAccount)
