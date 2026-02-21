import pytest
from users.services import AuthService
from users.models import User

@pytest.mark.django_db
class TestAuthService:
    def test_register_success(self):
        user, tokens = AuthService.register("test@test.com", "password123")
        assert user.email == "test@test.com"
        assert "access" in tokens
        assert "refresh" in tokens

    def test_register_duplicate_email(self):
        AuthService.register("test@test.com", "password123")
        with pytest.raises(ValueError, match="already exists"):
            AuthService.register("test@test.com", "password123")

    def test_login_success(self):
        AuthService.register("test@test.com", "password123")
        user, tokens = AuthService.login_email("test@test.com", "password123")
        assert user.email == "test@test.com"
        assert "access" in tokens

    def test_login_invalid_password(self):
        AuthService.register("test@test.com", "password123")
        with pytest.raises(ValueError):
            AuthService.login_email("test@test.com", "wrongpass")
