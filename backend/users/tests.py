"""
Unit tests for AuthService.
Tests cover registration, login, and social authentication.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from users.services import AuthService
from users.models import SocialAccount

User = get_user_model()


class TestAuthService(TestCase):
    """Test cases for AuthService."""

    def setUp(self):
        self.test_email = 'test@example.com'
        self.test_password = 'securepassword123'
        self.test_username = 'testuser'

    def test_register_creates_user(self):
        """Test that register creates a new user."""
        user, tokens = AuthService.register(
            email=self.test_email,
            password=self.test_password,
            username=self.test_username
        )
        
        assert user.email == self.test_email
        assert user.username == self.test_username
        assert 'refresh' in tokens
        assert 'access' in tokens
        assert User.objects.filter(email=self.test_email).exists()

    def test_register_duplicate_email(self):
        """Test that register raises error for duplicate email."""
        AuthService.register(
            email=self.test_email,
            password=self.test_password
        )
        
        with pytest.raises(ValueError) as excinfo:
            AuthService.register(
                email=self.test_email,
                password=self.test_password
            )
        assert "already exists" in str(excinfo.value)

    def test_login_email_success(self):
        """Test successful email login."""
        AuthService.register(
            email=self.test_email,
            password=self.test_password
        )
        
        user, tokens = AuthService.login_email(
            email=self.test_email,
            password=self.test_password
        )
        
        assert user.email == self.test_email
        assert 'refresh' in tokens
        assert 'access' in tokens

    def test_login_email_invalid_credentials(self):
        """Test login with invalid credentials."""
        with pytest.raises(ValueError) as excinfo:
            AuthService.login_email(
                email='nonexistent@example.com',
                password='wrongpassword'
            )
        assert "Invalid credentials" in str(excinfo.value)

    def test_login_email_wrong_password(self):
        """Test login with wrong password."""
        AuthService.register(
            email=self.test_email,
            password=self.test_password
        )
        
        with pytest.raises(ValueError) as excinfo:
            AuthService.login_email(
                email=self.test_email,
                password='wrongpassword'
            )
        assert "Invalid credentials" in str(excinfo.value)

    @patch('users.services.jwt.decode')
    @patch('users.services.PyJWKClient')
    def test_google_login_new_user(self, mock_jwks_client, mock_jwt_decode):
        """Test Google login for new user."""
        # Mock JWT decode
        mock_jwt_decode.return_value = {
            'email': 'google@example.com',
            'sub': 'google123'
        }
        
        # Mock JWKS client
        mock_key = MagicMock()
        mock_key.key = 'fake_key'
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value = mock_key
        
        user, tokens = AuthService.google_login('fake_token')
        
        assert user.email == 'google@example.com'
        assert SocialAccount.objects.filter(
            provider='GOOGLE',
            provider_user_id='google123'
        ).exists()

    @patch('users.services.jwt.decode')
    @patch('users.services.PyJWKClient')
    def test_google_login_existing_user(self, mock_jwks_client, mock_jwt_decode):
        """Test Google login for existing user."""
        # Create social account first
        user = User.objects.create_user(
            username='existing',
            email='google@example.com'
        )
        SocialAccount.objects.create(
            user=user,
            provider='GOOGLE',
            provider_user_id='google123',
            email='google@example.com'
        )
        
        # Mock JWT decode
        mock_jwt_decode.return_value = {
            'email': 'google@example.com',
            'sub': 'google123'
        }
        
        # Mock JWKS client
        mock_key = MagicMock()
        mock_key.key = 'fake_key'
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value = mock_key
        
        logged_user, tokens = AuthService.google_login('fake_token')
        
        assert logged_user.id == user.id

    @patch('users.services.jwt.decode')
    @patch('users.services.PyJWKClient')
    def test_google_login_expired_token(self, mock_jwks_client, mock_jwt_decode):
        """Test Google login with expired token."""
        import jwt
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")
        
        mock_key = MagicMock()
        mock_key.key = 'fake_key'
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value = mock_key
        
        with pytest.raises(ValueError) as excinfo:
            AuthService.google_login('fake_token')
        assert "expired" in str(excinfo.value).lower()

    @patch('users.services.jwt.decode')
    @patch('users.services.PyJWKClient')
    def test_apple_login_new_user(self, mock_jwks_client, mock_jwt_decode):
        """Test Apple login for new user."""
        # Mock JWT decode
        mock_jwt_decode.return_value = {
            'email': 'apple@example.com',
            'sub': 'apple123'
        }
        
        # Mock JWKS client
        mock_key = MagicMock()
        mock_key.key = 'fake_key'
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value = mock_key
        
        user, tokens = AuthService.apple_login('fake_token')
        
        assert user.email == 'apple@example.com'
        assert SocialAccount.objects.filter(
            provider='APPLE',
            provider_user_id='apple123'
        ).exists()

    @patch('users.services.jwt.decode')
    @patch('users.services.PyJWKClient')
    def test_apple_login_invalid_token(self, mock_jwks_client, mock_jwt_decode):
        """Test Apple login with invalid token."""
        import jwt
        mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid token")
        
        mock_key = MagicMock()
        mock_key.key = 'fake_key'
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value = mock_key
        
        with pytest.raises(ValueError) as excinfo:
            AuthService.apple_login('fake_token')
        assert "Invalid" in str(excinfo.value)

    def test_generate_tokens(self):
        """Test token generation."""
        user = User.objects.create_user(
            username='tokentest',
            email='token@example.com',
            password='password'
        )
        
        tokens = AuthService._generate_tokens(user)
        
        assert 'refresh' in tokens
        assert 'access' in tokens
        assert len(tokens['refresh']) > 0
        assert len(tokens['access']) > 0
