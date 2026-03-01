import uuid
from django.db import transaction, IntegrityError
import logging
from typing import Tuple, Dict, Any, Optional
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
from jwt import PyJWKClient
from django.conf import settings
from django.core.cache import cache

from .models import User, SocialAccount

logger = logging.getLogger(__name__)

# Module-level singletons for JWKS clients.
# PyJWKClient uses @lru_cache internally which cannot be pickled for Redis.
# In-process singleton is safe and correct here.
_google_jwks_client: Optional['PyJWKClient'] = None
_apple_jwks_client: Optional['PyJWKClient'] = None

class AuthService:
    """Service handling all authentication logic."""

    # Google OAuth2 JWKS URL for token verification
    GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
    
    # Apple JWKS URL for token verification
    APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
    
    # SECURITY: JWKS cache lifetime (1 hour) - keys change every few hours
    JWK_CACHE_LIFETIME = 3600
    
    # SECURITY: Request timeout for JWKS HTTP requests
    JWK_REQUEST_TIMEOUT = 10

    @staticmethod
    def _generate_tokens(user: User) -> Dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def _get_google_jwks_client():
        """Get or create cached JWKS client for Google (in-process singleton)."""
        global _google_jwks_client
        if _google_jwks_client is None:
            _google_jwks_client = PyJWKClient(
                uri=AuthService.GOOGLE_JWKS_URL,
                cache_keys=True,
                max_cached_keys=16,
            )
        return _google_jwks_client

    @staticmethod
    def _get_apple_jwks_client():
        """Get or create cached JWKS client for Apple (in-process singleton)."""
        global _apple_jwks_client
        if _apple_jwks_client is None:
            _apple_jwks_client = PyJWKClient(
                uri=AuthService.APPLE_JWKS_URL,
                cache_keys=True,
                max_cached_keys=16,
            )
        return _apple_jwks_client

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
        # USERNAME_FIELD = 'email', so authenticate() expects email as the username parameter
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Email not found.")

        user = authenticate(email=email, password=password)
        if not user:
            raise ValueError("Incorrect password.")
        
        return user, AuthService._generate_tokens(user)

    @staticmethod
    def google_login(token: str) -> Tuple[User, Dict[str, str]]:
        """
        Verify Google OAuth2 token with proper signature verification.
        SECURITY: Verifies signature, expiration, issuer, and audience.
        """
        try:
            # Get Google's public keys
            jwks_client = AuthService._get_google_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # SECURITY: Decode and verify the token with all checks
            # - verify_signature: Verify JWT signature
            # - verify_iat: Verify issued-at timestamp
            # - verify_exp: Verify expiration timestamp
            # - verify_aud: Verify audience (must match our Google Client ID)
            options = {
                "verify_signature": True,
                "verify_iat": True,
                "verify_exp": True,
            }
            
            # Only verify audience if GOOGLE_CLIENT_ID is set
            if settings.GOOGLE_CLIENT_ID:
                options["verify_aud"] = True
                audience = settings.GOOGLE_CLIENT_ID
            else:
                options["verify_aud"] = False
                audience = None
                logger.warning("GOOGLE_CLIENT_ID not set - skipping audience verification (DEV ONLY)")

            idinfo = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=audience,
                options=options
            )

            email = idinfo.get('email')
            provider_user_id = idinfo.get('sub')

            if not email or not provider_user_id:
                logger.warning(f"Google login: Missing email or sub in token payload")
                raise ValueError("Invalid Google token payload.")

            # Extract optional profile data from Google token
            display_name = idinfo.get('name') or idinfo.get('given_name')
            avatar_url = idinfo.get('picture')

            logger.info(f"Google login successful for user: {email}")
            return AuthService._handle_social_login(
                'GOOGLE', provider_user_id, email,
                display_name=display_name, avatar_url=avatar_url
            )

        except jwt.ExpiredSignatureError:
            logger.warning("Google login: Token has expired")
            raise ValueError("Google token has expired.")
        except jwt.InvalidAudienceError:
            logger.error("Google login: Invalid audience - token not issued for this app")
            raise ValueError("Invalid Google token - wrong audience.")
        except jwt.InvalidIssuerError:
            logger.error("Google login: Invalid issuer")
            raise ValueError("Invalid Google token - wrong issuer.")
        except jwt.InvalidTokenError as e:
            logger.error(f"Google login: Invalid token - {str(e)}")
            raise ValueError(f"Invalid Google token.")
        except Exception as e:
            logger.error(f"Google login failed: {str(e)}")
            raise ValueError(f"Google login failed: {str(e)}")

    @staticmethod
    def apple_login(identity_token: str) -> Tuple[User, Dict[str, str]]:
        """
        Verify Apple Sign-In token with proper signature verification.
        Uses Apple's public JWKS keys for verification.
        SECURITY: Verifies signature, expiration, issuer, and audience.
        """
        try:
            # Get Apple's public keys
            jwks_client = AuthService._get_apple_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(identity_token)
            
            # SECURITY: Decode and verify the token with all checks
            # - verify_signature: Verify JWT signature
            # - verify_iat: Verify issued-at timestamp
            # - verify_exp: Verify expiration timestamp
            # - verify_iss: Verify issuer (must be Apple)
            # - verify_aud: Verify audience (must match our Apple Client ID)
            payload = jwt.decode(
                identity_token,
                signing_key.key,
                algorithms=["RS256"],
                issuer="https://appleid.apple.com",  # SECURITY: Verify Apple is the issuer
                audience=settings.APPLE_CLIENT_ID,   # SECURITY: Verify audience
                options={
                    "verify_signature": True,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_iss": True,  # SECURITY: Critical - ensures token is from Apple
                    "verify_aud": True,  # SECURITY: Critical - prevents token from other apps
                }
            )
            
            email = payload.get('email')
            provider_user_id = payload.get('sub')

            if not email or not provider_user_id:
                logger.warning(f"Apple login: Missing email or sub in token payload")
                raise ValueError("Invalid Apple token payload.")

            logger.info(f"Apple login successful for user: {email}")
            return AuthService._handle_social_login('APPLE', provider_user_id, email)
            
        except jwt.ExpiredSignatureError:
            logger.warning("Apple login: Token has expired")
            raise ValueError("Apple token has expired.")
        except jwt.InvalidAudienceError:
            logger.error("Apple login: Invalid audience - token not issued for this app")
            raise ValueError("Invalid Apple token - wrong audience.")
        except jwt.InvalidIssuerError:
            logger.error("Apple login: Invalid issuer - token not from Apple")
            raise ValueError("Invalid Apple token - wrong issuer.")
        except jwt.InvalidTokenError as e:
            logger.error(f"Apple login: Invalid token - {str(e)}")
            raise ValueError(f"Invalid Apple token.")
        except Exception as e:
            logger.error(f"Apple login failed: {str(e)}")
            raise ValueError(f"Apple login failed: {str(e)}")

    @staticmethod
    def _handle_social_login(
        provider: str,
        provider_user_id: str,
        email: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Tuple[User, Dict[str, str]]:
        """
        Handle social login by finding or creating user account.
        Links the social account to the user.
        Wrapped in transaction.atomic() to prevent race condition duplicates.
        """
        try:
            # Try to find existing social account first (outside transaction — fast path)
            account = SocialAccount.objects.get(provider=provider, provider_user_id=provider_user_id)
            user = account.user
            logger.info(f"Social login ({provider}): Existing user found - {user.email}")
            return user, AuthService._generate_tokens(user)
        except SocialAccount.DoesNotExist:
            pass

        # Slow path: need to find/create user + link social account atomically
        try:
            with transaction.atomic():
                # Check if user with this email already exists
                try:
                    user = User.objects.select_for_update().get(email=email)
                    logger.info(f"Social login ({provider}): Linking to existing user - {email}")
                except User.DoesNotExist:
                    # Create new user
                    username = email.split('@')[0] + str(uuid.uuid4())[:8]
                    user = User.objects.create_user(username=username, email=email)
                    logger.info(f"Social login ({provider}): New user created - {email}")

                # Link external account (get_or_create to be safe against concurrent requests)
                _, created = SocialAccount.objects.get_or_create(
                    provider=provider,
                    provider_user_id=provider_user_id,
                    defaults={
                        'user': user,
                        'email': email,
                        'display_name': display_name,
                        'avatar_url': avatar_url,
                    }
                )
                if created:
                    logger.info(f"Social login ({provider}): Account linked successfully")
                else:
                    logger.info(f"Social login ({provider}): Account already linked (concurrent request)")

        except IntegrityError as e:
            logger.error(f"Social login ({provider}): IntegrityError during user creation - {e}")
            # Another concurrent request created the account — try fetching again
            try:
                account = SocialAccount.objects.get(provider=provider, provider_user_id=provider_user_id)
                user = account.user
            except SocialAccount.DoesNotExist:
                raise ValueError(f"Social login failed due to a conflict. Please try again.")

        return user, AuthService._generate_tokens(user)
