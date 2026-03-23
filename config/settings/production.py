from .base import *  # noqa: F401,F403

DEBUG = False

# --- Validate SECRET_KEY ---
if SECRET_KEY == "dev-only-insecure-key-do-not-use-in-production":  # noqa: F405
    raise ValueError(
        "DJANGO_SECRET_KEY is not set. "
        "Production MUST use a strong, unique secret key via environment variable."
    )

# --- SSL / HTTPS enforcement ---

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REDIRECT_EXEMPT = [r"^health/$"]

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 86400

CSRF_TRUSTED_ORIGINS = [
    "https://resume.get-hub.io",
]

# --- Additional security headers ---

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Permissions-Policy: restrict browser features
PERMISSIONS_POLICY = {
    "camera": [],
    "microphone": [],
    "geolocation": [],
    "payment": ["self"],
}

# --- Production logging ---

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
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
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
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

# --- S3-compatible storage (Hetzner Object Storage) ---

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
