from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Console email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable SSL in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0", "localhost"]

# Local PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "lebenslauf_db"),  # noqa: F405
        "USER": os.environ.get("POSTGRES_USER", "lebenslauf_user"),  # noqa: F405
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "localdevpassword123"),  # noqa: F405
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),  # noqa: F405
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),  # noqa: F405
    }
}

# Local Redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/0"),  # noqa: F405
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/1"),  # noqa: F405
        "KEY_PREFIX": "lb_session",
    },
}

# Run Celery tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Relaxed CSP for development
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'", "'unsafe-eval'"),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:", "blob:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'",),
        "frame-src": ("'self'",),
    }
}

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
            "level": "WARNING",
        },
    },
}
