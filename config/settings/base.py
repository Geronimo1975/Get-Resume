import os
from pathlib import Path
from datetime import timedelta
from django.urls import reverse_lazy

# Build paths: BASE_DIR = project root (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key-do-not-use-in-production")

DEBUG = False

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")


# --- Application definition ---

DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "csp",
    "django_celery_beat",
    "meta",
    "storages",
    "encrypted_model_fields",
]

LOCAL_APPS = [
    "accounts",
    "documents",
    "legal",
    "ats",
    "jobs",
    "coverletters",
    "emails",
    "pipeline",
    "payments",
    "blog",
    "automation",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# --- Middleware (ORDER MATTERS) ---

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]


# --- URL configuration ---

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# --- Templates ---

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
                "legal.context_processors.cookie_consent",
                "accounts.context_processors.subscription_status",
            ],
        },
    },
]


# --- Database (PostgreSQL) ---

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "lebenslauf_db"),
        "USER": os.environ.get("POSTGRES_USER", "lebenslauf_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}


# --- Cache (Redis) ---

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/0"),
        "KEY_PREFIX": "lb",
        "TIMEOUT": 300,
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_SESSION_URL", os.environ.get("REDIS_URL", "redis://redis:6379/0")).replace("/0", "/1"),
        "KEY_PREFIX": "lb_session",
        "TIMEOUT": 86400,
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"


# --- Celery ---

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/2")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/3")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Berlin"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 240
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    # Will be populated as apps are added
}


# --- Authentication (django-allauth, email-based) ---

AUTH_USER_MODEL = "accounts.User"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth v65+ settings
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_ADAPTER = "accounts.adapter.CustomAccountAdapter"
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/300s",
    "signup": "5/300s",
    "confirm_email": "3/180s",
}

LOGIN_REDIRECT_URL = "/mein-bereich/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/konto/anmelden/"


# --- Password validation ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Email ---
# Supports SMTP (default, DSGVO-compliant with EU providers like Brevo/Mailjet)
# and AWS SES (set EMAIL_BACKEND_TYPE=ses in env)

_email_backend_type = os.environ.get("EMAIL_BACKEND_TYPE", "smtp")

if _email_backend_type == "ses":
    EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
    ANYMAIL = {
        "AMAZON_SES_CLIENT_PARAMS": {
            "aws_access_key_id": os.environ.get("AWS_SES_ACCESS_KEY_ID", ""),
            "aws_secret_access_key": os.environ.get("AWS_SES_SECRET_ACCESS_KEY", ""),
            "region_name": os.environ.get("AWS_SES_REGION", "eu-central-1"),
        },
    }
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp-relay.brevo.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@get-hub.io")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "noreply@get-hub.io")


# --- Internationalization (German market) ---

LANGUAGE_CODE = "de"

LANGUAGES = [
    ("de", "Deutsch"),
    ("en", "English"),
]

TIME_ZONE = "Europe/Berlin"

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# --- Static & Media files ---

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024


# --- Unfold Admin UI ---

def _unfold_environment_callback(request):
    """Show environment badge in admin header."""
    env = os.environ.get("DJANGO_ENVIRONMENT", "local")
    if env == "production":
        return ["Produktion", "danger"]
    elif env == "staging":
        return ["Staging", "warning"]
    return ["Entwicklung", "info"]


UNFOLD = {
    "SITE_TITLE": "Lebenslauf-Builder",
    "SITE_HEADER": "Lebenslauf-Builder",
    "SITE_URL": "/",
    "SITE_SYMBOL": "description",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "config.settings.base._unfold_environment_callback",
    "COLORS": {
        "primary": {
            "50": "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "14 165 233",
            "600": "2 132 199",
            "700": "3 105 161",
            "800": "7 89 133",
            "900": "12 74 110",
            "950": "8 47 73",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Übersicht",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Benutzer",
                "items": [
                    {
                        "title": "Benutzer",
                        "icon": "people",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                ],
            },
            {
                "title": "Dokumente",
                "items": [
                    {
                        "title": "Dokumente",
                        "icon": "description",
                        "link": reverse_lazy("admin:documents_document_changelist"),
                    },
                    {
                        "title": "Vorlagen",
                        "icon": "style",
                        "link": reverse_lazy("admin:documents_template_changelist"),
                    },
                    {
                        "title": "Abschnitte",
                        "icon": "view_list",
                        "link": reverse_lazy("admin:documents_section_changelist"),
                    },
                ],
            },
        ],
    },
}


# --- Security defaults ---

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True


# --- Content Security Policy (django-csp v4) ---

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'"),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:", "blob:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'", "https://api.stripe.com"),
        "frame-src": ("'self'", "https://js.stripe.com"),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    }
}


# --- CORS ---

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "https://lebenslauf-builder.de,http://localhost:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True


# --- REST Framework ---

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "120/minute",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# --- JWT ---

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# --- dj-rest-auth ---

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
    "REGISTER_SERIALIZER": "accounts.serializers.CustomRegisterSerializer",
    "USER_DETAILS_SERIALIZER": "accounts.serializers.UserSerializer",
}


# --- drf-spectacular (API docs) ---

SPECTACULAR_SETTINGS = {
    "TITLE": "GetResume API",
    "DESCRIPTION": "Lebenslauf-Builder + Job Automation API for the German Market",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# --- Brevo CRM ---

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")


# --- Anthropic (Claude API) ---

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")


# --- Apify ---

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
APIFY_WEBHOOK_SECRET = os.environ.get("APIFY_WEBHOOK_SECRET", "")


# --- Stripe ---

STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_CURRENCY = "eur"

STRIPE_PRICE_IDS = {
    "premium_monthly": os.environ.get("STRIPE_PRICE_PREMIUM_MONTHLY", ""),
    "premium_yearly": os.environ.get("STRIPE_PRICE_PREMIUM_YEARLY", ""),
    "business": os.environ.get("STRIPE_PRICE_BUSINESS", ""),
}


# --- Sentry ---

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
        send_default_pii=False,
        environment=os.environ.get("DJANGO_ENVIRONMENT", "production"),
    )


# --- django-meta (SEO) ---

META_SITE_PROTOCOL = "https"
META_SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "lebenslauf-builder.de")
META_SITE_NAME = "Lebenslauf-Builder"
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True


# --- WeasyPrint ---

WEASYPRINT_BASEURL = os.environ.get("WEASYPRINT_BASEURL", "http://web:8000")
PDF_CACHE_TIMEOUT = 3600


# --- Cookie consent ---

COOKIE_CONSENT_NAME = "cookie_consent"
COOKIE_CONSENT_MAX_AGE = 365 * 24 * 60 * 60
COOKIE_CONSENT_IP_SALT = os.environ.get(
    "COOKIE_CONSENT_IP_SALT", "change-this-salt-in-production"
)
COOKIE_CONSENT_BANNER_VERSION = "1.0"


# --- Default primary key ---

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
