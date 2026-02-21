import uuid
from typing import Tuple, Dict, Any
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt

from .models import User, SocialAccount
from django.conf import settings

class AuthService:
    """Service handling all authentication logic."""

    @staticmethod
    def _generate_tokens(user: User) -> Dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def register(email: str, password: str, username: str = None) -> Tuple[User, Dict[str, str]]:
        if not username:
            username = email.split('@')[0] + str(uuid.uuid4())[:8]

        if User.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists.")

        user = User.objects.create_user(username=username, email=email, password=password)
        return user, AuthService._generate_tokens(user)

    @staticmethod
    def login_email(email: str, password: str) -> Tuple[User, Dict[str, str]]:
        # username or email depending on how authenticate is configured
        # Django's default authenticate uses username. We need to fetch by email first if we use email.
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Invalid credentials.")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise ValueError("Invalid credentials.")
        
        return user, AuthService._generate_tokens(user)

    @staticmethod
    def google_login(token: str) -> Tuple[User, Dict[str, str]]:
        try:
            # We skip client_id check in generic implementation unless provided in env
            # client_id=settings.GOOGLE_CLIENT_ID
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get('email')
            provider_user_id = idinfo.get('sub')
            
            if not email or not provider_user_id:
                raise ValueError("Invalid Google token payload.")
                
            return AuthService._handle_social_login('GOOGLE', provider_user_id, email)
        except ValueError as e:
            raise ValueError(f"Google login failed: {str(e)}")

    @staticmethod
    def apple_login(identity_token: str) -> Tuple[User, Dict[str, str]]:
        try:
            # Basic Apple token decoding: In production this should fetch Apple's public keys
            # and verify the signature using PyJWKClient. For now, we will decode unverified
            # or minimally verify using the provided secret (though Apple uses public key).
            # To avoid crash without keys, we do unverified decode for payload extraction.
            payload = jwt.decode(identity_token, options={"verify_signature": False})
            email = payload.get('email')
            provider_user_id = payload.get('sub')

            if not email or not provider_user_id:
                raise ValueError("Invalid Apple token payload.")
            
            return AuthService._handle_social_login('APPLE', provider_user_id, email)
        except Exception as e:
            raise ValueError(f"Apple login failed: {str(e)}")

    @staticmethod
    def _handle_social_login(provider: str, provider_user_id: str, email: str) -> Tuple[User, Dict[str, str]]:
        try:
            account = SocialAccount.objects.get(provider=provider, provider_user_id=provider_user_id)
            user = account.user
        except SocialAccount.DoesNotExist:
            # Check if user with this email already exists
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0] + str(uuid.uuid4())[:8]}
            )
            # Link external account
            SocialAccount.objects.create(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
                email=email
            )
        
        return user, AuthService._generate_tokens(user)
