# Django Settings & Docker Configuration Reference

Complete settings files and Docker Compose setup for the Lebenslauf-Builder platform.

---

## Settings Module Structure

```
config/
  settings/
    __init__.py       # Imports from environment-specific module
    base.py           # Shared settings for all environments
    local.py          # Development overrides
    production.py     # Production security and performance
```

---

## base.py

```python
# config/settings/base.py

import os
from pathlib import Path
from datetime import timedelta

# Build paths: BASE_DIR = project root (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")


# ──────────────────────────────────────────────
# Application definition
# ──────────────────────────────────────────────

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",          # Required by django-allauth
    "django.contrib.sitemaps",
    "django.contrib.postgres",       # PostgreSQL full-text search
]

THIRD_PARTY_APPS = [
    # Authentication
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # API
    "rest_framework",
    "corsheaders",
    # Frontend
    "django_htmx",
    # Security
    "csp",
    # Tasks
    "django_celery_beat",
    # SEO
    "meta",
    # Storage
    "storages",
    # Other
    "widget_tweaks",                  # Form rendering helpers
]

LOCAL_APPS = [
    "accounts",
    "documents",
    "payments",
    "editor",
    "blog",
    "legal",
    "api",
    "dashboard",
    "automation",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ──────────────────────────────────────────────
# Middleware (ORDER MATTERS)
# ──────────────────────────────────────────────

MIDDLEWARE = [
    # 1. Security headers (HSTS, X-Content-Type, etc.)
    "django.middleware.security.SecurityMiddleware",
    # 2. Static file serving (before session to avoid session overhead on statics)
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # 3. Session handling
    "django.contrib.sessions.middleware.SessionMiddleware",
    # 4. Content Security Policy headers
    "csp.middleware.CSPMiddleware",
    # 5. Cookie consent — blocks tracking scripts pre-consent (TTDSG §25)
    "legal.middleware.CookieConsentMiddleware",
    # 6. CORS headers for API
    "corsheaders.middleware.CorsMiddleware",
    # 7. Common (URL normalization, forbidden hosts)
    "django.middleware.common.CommonMiddleware",
    # 8. CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    # 9. Authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # 10. Flash messages
    "django.contrib.messages.middleware.MessageMiddleware",
    # HTMX middleware (detects hx-request header)
    "django_htmx.middleware.HtmxMiddleware",
    # Allauth middleware
    "allauth.account.middleware.AccountMiddleware",
]


# ──────────────────────────────────────────────
# URL configuration
# ──────────────────────────────────────────────

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# ──────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                # Custom: inject cookie consent status into all templates
                "legal.context_processors.cookie_consent",
                # Custom: inject subscription status
                "accounts.context_processors.subscription_status",
            ],
        },
    },
]


# ──────────────────────────────────────────────
# Database — PostgreSQL
# ──────────────────────────────────────────────

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "lebenslauf_db"),
        "USER": os.environ.get("POSTGRES_USER", "lebenslauf_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 600,  # 10 minutes persistent connections
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}


# ──────────────────────────────────────────────
# Cache — Redis
# ──────────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/0"),
        "OPTIONS": {
            "db": 0,
        },
        "KEY_PREFIX": "lb",
        "TIMEOUT": 300,  # 5 minutes default
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/1"),
        "KEY_PREFIX": "lb_session",
        "TIMEOUT": 86400,  # 24 hours
    },
}

# Use Redis for sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"


# ──────────────────────────────────────────────
# Celery — Task Queue
# ──────────────────────────────────────────────

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/2")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/3")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Berlin"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes soft limit
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Celery Beat schedule (periodic tasks)
CELERY_BEAT_SCHEDULE = {
    "check-expiring-subscriptions": {
        "task": "payments.tasks.check_expiring_subscriptions",
        "schedule": timedelta(hours=6),
    },
    "gdpr-cleanup-soft-deleted": {
        "task": "legal.tasks.gdpr_cleanup_soft_deleted",
        "schedule": timedelta(days=1),
    },
    "generate-sitemap": {
        "task": "blog.tasks.generate_sitemap",
        "schedule": timedelta(hours=12),
    },
}


# ──────────────────────────────────────────────
# Authentication — django-allauth (email-based)
# ──────────────────────────────────────────────

AUTH_USER_MODEL = "accounts.User"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes lockout

LOGIN_REDIRECT_URL = "/mein-bereich/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/konto/anmelden/"


# ──────────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ──────────────────────────────────────────────
# Email — AWS SES via django-anymail
# ──────────────────────────────────────────────

EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": os.environ.get("AWS_SES_ACCESS_KEY_ID", ""),
        "aws_secret_access_key": os.environ.get("AWS_SES_SECRET_ACCESS_KEY", ""),
        "region_name": os.environ.get("AWS_SES_REGION", "eu-central-1"),
    },
}
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "noreply@lebenslauf-builder.de"
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "server@lebenslauf-builder.de")


# ──────────────────────────────────────────────
# Internationalization — German market
# ──────────────────────────────────────────────

LANGUAGE_CODE = "de"

LANGUAGES = [
    ("de", "Deutsch"),
    ("en", "English"),
]

TIME_ZONE = "Europe/Berlin"

USE_I18N = True
USE_L10N = True  # German number/date formatting (e.g., 1.000,00)
USE_TZ = True    # All timestamps stored in UTC

LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# ──────────────────────────────────────────────
# Static & Media files
# ──────────────────────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# WhiteNoise for production static file serving
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Max upload size (5MB for photos)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024


# ──────────────────────────────────────────────
# Security defaults (hardened in production.py)
# ──────────────────────────────────────────────

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True


# ──────────────────────────────────────────────
# Content Security Policy (django-csp)
# ──────────────────────────────────────────────

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # HTMX requires inline
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")   # Tailwind + inline styles
CSP_IMG_SRC = ("'self'", "data:", "blob:")
CSP_FONT_SRC = ("'self'",)  # Self-hosted fonts only (LG Muenchen ruling)
CSP_CONNECT_SRC = ("'self'", "https://api.stripe.com")
CSP_FRAME_SRC = ("'self'", "https://js.stripe.com")
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)


# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "https://lebenslauf-builder.de"
).split(",")
CORS_ALLOW_CREDENTIALS = True


# ──────────────────────────────────────────────
# REST Framework
# ──────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "120/minute",
    },
}


# ──────────────────────────────────────────────
# Stripe
# ──────────────────────────────────────────────

STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_CURRENCY = "eur"

# Price IDs for subscription plans
STRIPE_PRICE_IDS = {
    "premium_monthly": os.environ.get("STRIPE_PRICE_PREMIUM_MONTHLY", ""),
    "premium_yearly": os.environ.get("STRIPE_PRICE_PREMIUM_YEARLY", ""),
    "business": os.environ.get("STRIPE_PRICE_BUSINESS", ""),
}


# ──────────────────────────────────────────────
# Sentry (error tracking)
# ──────────────────────────────────────────────

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,  # DSGVO: do not send PII to Sentry
        environment=os.environ.get("DJANGO_ENVIRONMENT", "production"),
    )


# ──────────────────────────────────────────────
# django-meta (SEO)
# ──────────────────────────────────────────────

META_SITE_PROTOCOL = "https"
META_SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "lebenslauf-builder.de")
META_SITE_NAME = "Lebenslauf-Builder"
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True


# ──────────────────────────────────────────────
# WeasyPrint / PDF generation
# ──────────────────────────────────────────────

WEASYPRINT_BASEURL = os.environ.get("WEASYPRINT_BASEURL", "http://web:8000")

# PDF cache timeout (seconds). Invalidated on content change.
PDF_CACHE_TIMEOUT = 3600  # 1 hour


# ──────────────────────────────────────────────
# Cookie consent settings
# ──────────────────────────────────────────────

COOKIE_CONSENT_NAME = "cookie_consent"
COOKIE_CONSENT_MAX_AGE = 365 * 24 * 60 * 60  # 1 year
COOKIE_CONSENT_IP_SALT = os.environ.get(
    "COOKIE_CONSENT_IP_SALT", "change-this-salt-in-production"
)
COOKIE_CONSENT_BANNER_VERSION = "1.0"


# ──────────────────────────────────────────────
# Default primary key field type
# ──────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

---

## local.py

```python
# config/settings/local.py

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Use console email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable SSL in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Show debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0", "localhost"]

# Use local PostgreSQL or SQLite for quick tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "lebenslauf_db"),  # noqa: F405
        "USER": os.environ.get("POSTGRES_USER", "lebenslauf_user"),  # noqa: F405
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "localpassword"),  # noqa: F405
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),  # noqa: F405
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),  # noqa: F405
    }
}

# Local Redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),  # noqa: F405
    }
}

# Celery: run tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Relaxed CSP for development
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")

# Stripe test keys
STRIPE_PUBLISHABLE_KEY = os.environ.get(  # noqa: F405
    "STRIPE_PUBLISHABLE_KEY", "pk_test_..."
)
STRIPE_SECRET_KEY = os.environ.get(  # noqa: F405
    "STRIPE_SECRET_KEY", "sk_test_..."
)

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django.db.backends": {
            "level": "WARNING",  # Set to DEBUG to see SQL queries
        },
    },
}
```

---

## production.py

```python
# config/settings/production.py

from .base import *  # noqa: F401,F403

DEBUG = False

# ──────────────────────────────────────────────
# SSL / HTTPS enforcement
# ──────────────────────────────────────────────

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000       # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 86400  # 24 hours

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "https://lebenslauf-builder.de",
    "https://www.lebenslauf-builder.de",
]

# ──────────────────────────────────────────────
# Additional security headers
# ──────────────────────────────────────────────

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
PERMISSIONS_POLICY = {
    "camera": [],
    "microphone": [],
    "geolocation": [],
    "payment": ["self"],  # Allow Stripe payment API
}

# ──────────────────────────────────────────────
# Production logging
# ──────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "payments": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "legal": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ──────────────────────────────────────────────
# S3-compatible storage (Hetzner Object Storage)
# ──────────────────────────────────────────────

if os.environ.get("USE_S3_STORAGE", "false").lower() == "true":  # noqa: F405
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    AWS_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID", "")  # noqa: F405
    AWS_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", "")  # noqa: F405
    AWS_STORAGE_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "lebenslauf-media")  # noqa: F405
    AWS_S3_ENDPOINT_URL = os.environ.get(  # noqa: F405
        "S3_ENDPOINT_URL", "https://fsn1.your-objectstorage.com"
    )
    AWS_S3_REGION_NAME = os.environ.get("S3_REGION", "fsn1")  # noqa: F405
    AWS_DEFAULT_ACL = "private"
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600
```

---

## settings/__init__.py

```python
# config/settings/__init__.py

import os

environment = os.environ.get("DJANGO_ENVIRONMENT", "local")

if environment == "production":
    from .production import *  # noqa: F401,F403
else:
    from .local import *  # noqa: F401,F403
```

---

## docker-compose.yml

```yaml
# docker-compose.yml

version: "3.9"

services:
  # ── Django Web Application (Gunicorn) ──────────────
  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: >
      gunicorn config.wsgi:application
      --bind 0.0.0.0:8000
      --workers 3
      --threads 2
      --timeout 120
      --access-logfile -
      --error-logfile -
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DJANGO_ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # ── PostgreSQL Database ────────────────────────────
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - .env
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-lebenslauf_db}
      POSTGRES_USER: ${POSTGRES_USER:-lebenslauf_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-lebenslauf_user} -d ${POSTGRES_DB:-lebenslauf_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s

  # ── Redis (Cache + Celery Broker) ──────────────────
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Celery Worker ──────────────────────────────────
  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: >
      celery -A config worker
      --loglevel=info
      --concurrency=2
      --max-tasks-per-child=1000
      -Q default,payments,emails,gdpr
    volumes:
      - .:/app
      - media_volume:/app/media
    env_file:
      - .env
    environment:
      - DJANGO_ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # ── Celery Beat (Scheduler) ────────────────────────
  celery_beat:
    build:
      context: .
      dockerfile: Dockerfile
    command: >
      celery -A config beat
      --loglevel=info
      --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      - DJANGO_ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # ── Nginx Reverse Proxy ────────────────────────────
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local
```

---

## Dockerfile

```dockerfile
# Dockerfile

# ── Stage 1: Build dependencies ─────────────────────
FROM python:3.12-slim as builder

WORKDIR /app

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production image ───────────────────────
FROM python:3.12-slim

WORKDIR /app

# Runtime dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system django && adduser --system --group django
USER django

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## Nginx Configuration

```nginx
# nginx/conf.d/default.conf

upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name lebenslauf-builder.de www.lebenslauf-builder.de;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lebenslauf-builder.de www.lebenslauf-builder.de;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # Max upload size (for CV photos)
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files (user uploads — require auth via Django)
    location /media/ {
        internal;  # Only accessible via X-Accel-Redirect from Django
        alias /app/media/;
    }

    # Django application
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed for live preview)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint (no logging)
    location /health/ {
        proxy_pass http://django;
        access_log off;
    }
}
```

---

## .env.example

```bash
# .env.example
# Copy to .env and fill in all values.
# NEVER commit .env to version control!

# ─── Django ──────────────────────────────────────────
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DJANGO_ENVIRONMENT=local              # local | production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,lebenslauf-builder.de
DJANGO_DEBUG=True

# ─── Database (PostgreSQL) ───────────────────────────
POSTGRES_DB=lebenslauf_db
POSTGRES_USER=lebenslauf_user
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_HOST=db                       # 'db' for Docker, 'localhost' for local
POSTGRES_PORT=5432

# ─── Redis ───────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ─── Celery ──────────────────────────────────────────
CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3

# ─── Stripe ──────────────────────────────────────────
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PREMIUM_MONTHLY=price_...
STRIPE_PRICE_PREMIUM_YEARLY=price_...
STRIPE_PRICE_BUSINESS=price_...

# ─── Email (AWS SES) ────────────────────────────────
AWS_SES_ACCESS_KEY_ID=AKIA...
AWS_SES_SECRET_ACCESS_KEY=your-ses-secret-key
AWS_SES_REGION=eu-central-1
DEFAULT_FROM_EMAIL=noreply@lebenslauf-builder.de
SERVER_EMAIL=server@lebenslauf-builder.de

# ─── S3 Storage (Hetzner Object Storage) ────────────
USE_S3_STORAGE=false
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=lebenslauf-media
S3_ENDPOINT_URL=https://fsn1.your-objectstorage.com
S3_REGION=fsn1

# ─── Sentry ─────────────────────────────────────────
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1

# ─── Site ────────────────────────────────────────────
SITE_DOMAIN=lebenslauf-builder.de
CORS_ALLOWED_ORIGINS=https://lebenslauf-builder.de

# ─── Cookie Consent ─────────────────────────────────
COOKIE_CONSENT_IP_SALT=generate-a-random-salt-here

# ─── WeasyPrint ──────────────────────────────────────
WEASYPRINT_BASEURL=http://web:8000
```

---

## Celery Configuration

```python
# config/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("lebenslauf_builder")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Define task queues
app.conf.task_routes = {
    "payments.tasks.*": {"queue": "payments"},
    "legal.tasks.*": {"queue": "gdpr"},
    "automation.tasks.send_*": {"queue": "emails"},
}

# Retry policy for transient failures
app.conf.task_default_retry_delay = 60  # 1 minute
app.conf.task_max_retries = 3
```

```python
# config/__init__.py

from .celery import app as celery_app

__all__ = ("celery_app",)
```

---

## URL Configuration

```python
# config/urls.py

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path("admin-dashboard/", admin.site.urls),

    # Authentication (django-allauth)
    path("konto/", include("allauth.urls")),

    # App URLs
    path("", include("editor.urls")),
    path("mein-bereich/", include("dashboard.urls")),
    path("api/", include("api.urls")),
    path("karriere-blog/", include("blog.urls")),
    path("", include("legal.urls")),         # /impressum/, /datenschutz/, /agb/
    path("", include("payments.urls")),      # /preise/, /checkout/, /webhook/

    # Health check
    path(
        "health/",
        TemplateView.as_view(template_name="health.html"),
        name="health_check",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

# Customize admin site
admin.site.site_header = "Lebenslauf-Builder Admin"
admin.site.site_title = "Lebenslauf-Builder"
admin.site.index_title = "Verwaltung"
```
