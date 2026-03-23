"""Test settings — SQLite in-memory, no external services."""
from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

ALLOWED_HOSTS = ["*"]

# SQLite for fast isolated tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# In-memory cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "KEY_PREFIX": "lb_session",
    },
}

# Console email (captured by Django test client)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Celery runs synchronously but doesn't propagate errors from side-effect tasks
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False

# Disable throttling in tests
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405

# Speed up password hashing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Skip CSP in tests
CONTENT_SECURITY_POLICY = None

# Allauth — skip email verification for cleaner test flow override
ACCOUNT_EMAIL_VERIFICATION = "optional"
