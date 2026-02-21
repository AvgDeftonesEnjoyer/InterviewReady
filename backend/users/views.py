from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializer, LoginSerializer, SocialLoginSerializer, TokenResponseSerializer
from .services import AuthService

class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []

    @method_decorator(ratelimit(key='ip', rate='5/h', block=True))
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user, tokens = AuthService.register(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                username=serializer.validated_data.get('username')
            )
            data = {'user_id': user.id, **tokens}
            return Response(data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='10/h', block=True))
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user, tokens = AuthService.login_email(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            data = {'user_id': user.id, **tokens}
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, tokens = AuthService.google_login(serializer.validated_data['token'])
            data = {'user_id': user.id, **tokens}
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AppleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, tokens = AuthService.apple_login(serializer.validated_data['token'])
            data = {'user_id': user.id, **tokens}
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Alias for simplejwt refresh
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
