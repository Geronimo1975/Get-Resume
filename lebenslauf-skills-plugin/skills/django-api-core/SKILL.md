---
name: django-api-core
description: >
  This skill should be used when the user asks to "set up the Django project", "create models",
  "configure settings", "set up Docker", "create migrations", "configure the database",
  "add a new Django app", "set up DRF", "configure JWT auth", "create API endpoints",
  "set up CORS", or mentions Django setup, project structure, models, migrations,
  database schema, settings, Docker, REST API, serializers, viewsets, JWT authentication,
  PostgreSQL, Redis, Celery, project architecture, or any foundational backend work
  for the GetResume SaaS platform. Triggers on: Django, DRF, models, settings, migrations,
  URL routing, middleware, serializers, viewsets, JWT, CORS, PostgreSQL, Redis, Celery.
---

# Django API Core

Core Django 5 + Django REST Framework backend for the GetResume SaaS platform — a Lebenslauf-Builder + Job Automation platform targeting the German market.

## Architecture

**Vue.js SPA + Django REST API** — The frontend is a standalone Vue.js 3 SPA communicating with the Django backend exclusively through REST API endpoints. Django does NOT serve HTML templates to users (except for PDF rendering via WeasyPrint and blog pages for SEO).

## Project Structure

```
backend/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/         # User, Profile, Team, Auth (JWT)
│   ├── documents/        # Document, Template, Theme
│   ├── ats/              # ATS scoring + AI optimization
│   ├── jobs/             # ScrapedJob, ScrapingRun (Apify)
│   ├── coverletters/     # AI cover letter generation (Claude API)
│   ├── emails/           # EmailCredential, sending, IMAP tracking
│   ├── pipeline/         # JobApplication, ApplicationEmail
│   ├── payments/         # Subscription, Payment, Invoice (Stripe)
│   ├── legal/            # CookieConsent, GDPRRequest, AuditLog
│   ├── blog/             # BlogPost, Category, Tag
│   └── automation/       # Celery tasks, signals, webhook handlers
├── templates/            # PDF templates ONLY (WeasyPrint rendering)
│   └── pdf/
│       ├── lebenslauf/
│       ├── bewerbungsschreiben/
│       ├── deckblatt/
│       └── invoice/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── Dockerfile
└── docker-compose.yml
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Django 5.1 |
| API | Django REST Framework 3.15 |
| Auth | dj-rest-auth + djangorestframework-simplejwt |
| Social Auth | django-allauth (Google, LinkedIn OAuth) |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Task Queue | Celery 5 + django-celery-beat |
| Frontend | **Vue.js 3 SPA (separate project)** |
| PDF | WeasyPrint (server-side HTML → PDF) |
| AI | Claude API (Anthropic SDK) |
| Email | AWS SES via django-anymail |
| Storage | django-storages + S3 (Hetzner Object Storage) |
| Monitoring | Sentry, Prometheus |

## Key Settings

```python
# Locale
LANGUAGE_CODE = 'de'
TIME_ZONE = 'Europe/Berlin'
USE_L10N = True

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://getresume.de']

# CORS (Vue.js SPA)
CORS_ALLOWED_ORIGINS = ['https://getresume.de']
CORS_ALLOW_CREDENTIALS = True

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

## API URL Structure

```
/api/v1/
├── auth/           → JWT login, register, refresh, social auth
├── users/          → Profile, GDPR controls, email credentials
├── teams/          → B2B light: team management
├── documents/      → CV CRUD, PDF generation, preview
├── templates/      → Template catalog
├── themes/         → Color/font themes
├── jobs/           → Scraped jobs, scraping runs
├── coverletters/   → AI generation
├── applications/   → Pipeline tracking
├── payments/       → Stripe checkout, subscription, invoices
├── blog/           → Blog posts, categories
├── legal/          → Cookie consent, Impressum data
└── webhooks/       → Apify, Stripe, n8n callbacks
```

## Database Design Principles

- PostgreSQL with `JSONField` for CV content (flexible schema)
- UUID primary keys on all user-facing models
- Soft delete with `deleted_at` timestamp (DSGVO audit trail)
- All timestamps in UTC, displayed in Europe/Berlin
- Encrypted fields for sensitive data (django-encrypted-model-fields)
- Sequential invoice numbers (GoBD compliance)

## Middleware Stack

1. SecurityMiddleware
2. CorsMiddleware (django-cors-headers)
3. SessionMiddleware
4. CspMiddleware (django-csp)
5. CommonMiddleware
6. CsrfViewMiddleware
7. AuthenticationMiddleware

Note: Cookie consent is handled client-side in the Vue.js SPA (no server middleware needed).

## Dependencies

```
Django>=5.1
djangorestframework>=3.15
djangorestframework-simplejwt
dj-rest-auth[with-social]
django-allauth
django-cors-headers
django-csp
django-filter
django-encrypted-model-fields
django-anymail[amazon-ses]
django-storages[s3]
celery[redis]
django-celery-beat
WeasyPrint
Pillow
psycopg[binary]
redis
gunicorn
sentry-sdk
anthropic
openpyxl
```

## Additional Resources

### Reference Files

For detailed model schemas, settings templates, and Docker configuration:
- **`references/models.md`** — Complete model definitions for all apps
- **`references/settings-and-docker.md`** — Full settings templates and Docker Compose configuration
