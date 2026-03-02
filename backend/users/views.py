from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializer, LoginSerializer, SocialLoginSerializer, TokenResponseSerializer, OnboardingSerializer, ProfileUpdateSerializer
from .services import AuthService
from gamification.models import UserProfile


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []

    @method_decorator(ratelimit(key='ip', rate='20/h', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many registration attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, tokens = AuthService.register(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                username=serializer.validated_data.get('username')
            )
            profile = getattr(user, 'profile', None)
            data = {
                'user_id': user.id,
                'ui_language': getattr(profile, 'ui_language', 'en') if profile else 'en',
                'onboarding_completed': getattr(profile, 'onboarding_completed', False) if profile else False,
                **tokens
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/h', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many login attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user, tokens = AuthService.login_email(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            profile = getattr(user, 'profile', None)
            data = {
                'user_id': user.id, 
                'ui_language': getattr(profile, 'ui_language', 'en') if profile else 'en',
                'onboarding_completed': getattr(profile, 'onboarding_completed', False) if profile else False,
                **tokens
            }
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/h', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, tokens = AuthService.google_login(serializer.validated_data['token'])
            profile = getattr(user, 'profile', None)
            data = {
                'user_id': user.id,
                'email': user.email,
                'ui_language': getattr(profile, 'ui_language', 'en') if profile else 'en',
                'onboarding_completed': getattr(profile, 'onboarding_completed', False) if profile else False,
                **tokens
            }
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AppleLoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/h', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, tokens = AuthService.apple_login(serializer.validated_data['token'])
            profile = getattr(user, 'profile', None)
            data = {
                'user_id': user.id,
                'email': user.email,
                'ui_language': getattr(profile, 'ui_language', 'en') if profile else 'en',
                'onboarding_completed': getattr(profile, 'onboarding_completed', False) if profile else False,
                **tokens
            }
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Alias for simplejwt refresh
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='60/h', block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many refresh attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return super().post(request, *args, **kwargs)

class OnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get or create UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        profile.primary_language = serializer.validated_data['language']
        profile.specialization = serializer.validated_data['specialization']
        profile.experience_level = serializer.validated_data['experience_level']
        profile.onboarding_completed = True
        profile.save()
        
        return Response({'onboarding_completed': True}, status=status.HTTP_200_OK)

class UpdateLanguageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        lang = request.data.get('language')
        if lang not in ['en', 'uk']:
            return Response(
                {'error': 'Invalid language. Use: en, uk'},
                status=400
            )
        profile = request.user.profile
        profile.ui_language = lang
        profile.save()
        return Response({
            'language': lang,
            'message': 'Language updated successfully'
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)

        # Get avatar from linked social account (prefer Google, fallback to any)
        social = user.social_accounts.filter(provider='GOOGLE').first() \
                 or user.social_accounts.first()
        avatar_url = getattr(social, 'avatar_url', None)

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar_url': avatar_url,
            'primary_language': getattr(profile, 'primary_language', None),
            'specialization': getattr(profile, 'specialization', None),
            'experience_level': getattr(profile, 'experience_level', None),
            'ui_language': getattr(profile, 'ui_language', 'en'),
            'onboarding_completed': getattr(profile, 'onboarding_completed', False),
            'total_xp': getattr(profile, 'total_xp', 0),
            'current_level': getattr(profile, 'current_level', 1),
        })

    def patch(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(profile, field, value)

        profile.save()
        return Response({'message': 'Profile updated successfully'})
