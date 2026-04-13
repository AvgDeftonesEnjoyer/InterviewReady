import os
from pathlib import Path
import environ
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY: Validate required environment variables
required_env_vars = ['SECRET_KEY', 'OPENAI_API_KEY']
for var in required_env_vars:
    if not os.environ.get(var):
        raise ValueError(f"Required environment variable '{var}' is not set!")

# SECURITY: SECRET_KEY must be set in environment - no default allowed
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# SECURITY: Explicit allowed hosts - no wildcards in production
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '192.168.1.100', '0.0.0.0'])

# SECURITY: CSRF trusted origins for API
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'http://localhost:8081',
    'http://127.0.0.1:8081',
    'http://localhost:19006',  # Expo web
    # For LAN access on Expo mobile, add your full IP in .env:
    # CSRF_TRUSTED_ORIGINS=http://192.168.1.100:8081
])


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',

    # Local apps
    'core',
    'users',
    'subscriptions',
    'gamification',
    'progress',
    'learning',
    'ai',
    'interviews',
    'home',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'ai_requests': '30/hour',
    },
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    # SECURITY: Reduced token lifetimes for better security
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Reduced from 60
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),     # Reduced from 7
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    # Additional security
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/1')

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'recalculate-streaks-midnight': {
        'task': 'gamification.tasks.recalculate_streaks_task',
        'schedule': crontab(hour=0, minute=0),
    },
    'reset-ai-usage-midnight': {
        'task': 'ai.tasks.reset_daily_ai_usage_task',
        'schedule': crontab(hour=0, minute=0),
    },
    'generate-daily-challenges-midnight': {
        'task': 'gamification.tasks.generate_daily_challenges_task',
        'schedule': crontab(hour=0, minute=0),
    }
}

# Stripe (Android)
STRIPE_SECRET_KEY           = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET       = env('STRIPE_WEBHOOK_SECRET', default='')
STRIPE_PRO_MONTHLY_PRICE_ID = env('STRIPE_PRO_MONTHLY_PRICE_ID', default='')
STRIPE_PRO_ANNUAL_PRICE_ID  = env('STRIPE_PRO_ANNUAL_PRICE_ID', default='')
STRIPE_PRO_PLUS_MONTHLY_PRICE_ID = env('STRIPE_PRO_PLUS_MONTHLY_PRICE_ID', default='')
STRIPE_PRO_PLUS_ANNUAL_PRICE_ID  = env('STRIPE_PRO_PLUS_ANNUAL_PRICE_ID', default='')

# RevenueCat (iOS + Android verification)
REVENUECAT_API_KEY      = env('REVENUECAT_API_KEY', default='')
REVENUECAT_WEBHOOK_AUTH = env('REVENUECAT_WEBHOOK_AUTH', default='')

# Apple IAP
APPLE_SHARED_SECRET = env('APPLE_SHARED_SECRET', default='')
APPLE_CLIENT_ID = env('APPLE_CLIENT_ID', default='')
APPLE_BUNDLE_ID = env('APPLE_BUNDLE_ID', default='')

# Google/Stripe
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', default='')

# Plan pricing config
PLAN_PRICES = {
    'PRO': {
        'monthly': 4.99,
        'annual':  47.99,
    },
    'PRO_PLUS': {
        'monthly': 9.99,
        'annual':  95.99,
    },
}

# AI Models - configured models for different tasks
OPENAI_INTERVIEW_MODEL = env(
    'OPENAI_INTERVIEW_MODEL',
    default='gpt-4o-mini'
)
OPENAI_EVALUATION_MODEL = env(
    'OPENAI_EVALUATION_MODEL',
    default='gpt-4o-mini'
)
OPENAI_TRANSCRIPTION_MODEL = env(
    'OPENAI_TRANSCRIPTION_MODEL',
    default='whisper-1'
)

# SECURITY: CORS - restrict to specific origins only
CORS_ALLOW_ALL_ORIGINS = False  # Must be False in production
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
# Optional: Enable credentials if needed
CORS_ALLOW_CREDENTIALS = True

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
