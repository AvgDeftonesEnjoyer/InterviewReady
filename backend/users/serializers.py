from rest_framework import serializers

LANGUAGE_CHOICES = ['python', 'javascript', 'java', 'go', 'csharp']
SPECIALIZATION_CHOICES = ['backend', 'frontend', 'fullstack', 'data', 'ml']
EXPERIENCE_CHOICES = ['junior', 'middle', 'senior']
UI_LANGUAGE_CHOICES = ['en', 'uk']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SocialLoginSerializer(serializers.Serializer):
    token = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user_id = serializers.IntegerField()


class OnboardingSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES)
    specialization = serializers.ChoiceField(choices=SPECIALIZATION_CHOICES)
    experience_level = serializers.ChoiceField(choices=EXPERIENCE_CHOICES)


class ProfileUpdateSerializer(serializers.Serializer):
    """Serializer for PATCH /users/me/ to validate profile fields."""
    primary_language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, required=False)
    specialization = serializers.ChoiceField(choices=SPECIALIZATION_CHOICES, required=False)
    experience_level = serializers.ChoiceField(choices=EXPERIENCE_CHOICES, required=False)
    ui_language = serializers.ChoiceField(choices=UI_LANGUAGE_CHOICES, required=False)
