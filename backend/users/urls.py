from django.urls import path
from .views import RegisterView, LoginView, GoogleLoginView, AppleLoginView, CustomTokenRefreshView, OnboardingView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('apple/', AppleLoginView.as_view(), name='apple_login'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
]
