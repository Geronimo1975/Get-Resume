# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GetResume — a German-market SaaS CV/resume builder (`lebenslauf-builder.de`). Django 5.1 REST API backend + Vue 3 SPA frontend. All user-facing text is in German.

## Build & Run Commands

### Backend (Django)

```bash
# Dev server (requires PostgreSQL + Redis — use docker compose up db redis)
python3 manage.py runserver

# Database
python3 manage.py makemigrations
python3 manage.py migrate

# System check (verify all apps load)
python3 manage.py check

# Docker (full stack)
docker compose up              # web + db + redis
docker compose up --build      # rebuild image

# Celery (runs synchronously in dev via CELERY_TASK_ALWAYS_EAGER)
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend (Vue 3 / Vite)

```bash
cd frontend
nvm use              # Node 22 required (.nvmrc)
npm install
npm run dev          # http://localhost:3000 (proxies /api → :8000)
npm run build        # vite production build → dist/ (no vue-tsc type-check)
```

### Dev Setup

```bash
cp .env.example .env                    # then fill in values
docker compose up db redis              # start only DB + Redis
python3 manage.py migrate               # apply migrations
python3 manage.py createsuperuser       # admin access at /admin-dashboard/
docker compose exec db psql -U lebenslauf_user -d lebenslauf_db  # direct DB access
```

### Testing

```bash
# Run all tests (uses SQLite in-memory — no Docker needed)
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test -v 2

# Run specific app tests
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test accounts.tests -v 2
```

Test settings (`config/settings/test.py`) use SQLite, locmem email backend, MD5 password hasher for speed, and `CELERY_TASK_EAGER_PROPAGATES = False` to isolate from external services.

### API Docs

`drf-spectacular` is installed and configured but no URL route serves the schema/UI yet. To add it, mount `SpectacularAPIView` and `SpectacularSwaggerView` in `config/urls.py`.

## Architecture

### Settings System

`config/settings/__init__.py` selects `local.py` or `production.py` based on `DJANGO_ENVIRONMENT` env var (default: `local`). Both extend `base.py`. Local dev uses `CELERY_TASK_ALWAYS_EAGER = True` and console email backend.

### Authentication Flow

Email-only auth (no username). `django-allauth` → `dj-rest-auth` → `djangorestframework-simplejwt`. JWT tokens (30min access, 7d refresh with rotation + blacklist). Tokens are in JSON body, not HttpOnly cookies. Frontend stores in `localStorage` and auto-refreshes on 401 via Axios interceptor.

Custom adapter (`accounts.adapter.CustomAccountAdapter`) redirects allauth email confirmation URLs to the Vue SPA frontend via `FRONTEND_URL` env var.

### App Structure (11 Django apps)

- **accounts** — Custom `User` (UUID PK, email-based), `UserProfile` (auto-created via signal)
- **documents** — `Document` (JSONField content, soft delete), `Template`, `Section`
- **legal** — Cookie consent, GDPR request models (stub)
- **ats, jobs, coverletters, emails, pipeline, payments, blog, automation** — scaffolded with `apps.py`/`urls.py`/`models.py`, business logic not yet implemented

### Frontend Structure

Vue 3 Composition API with `<script setup lang="ts">`. `@/` alias maps to `src/`.

- `api/client.ts` — Axios instance, JWT interceptors, `baseURL: '/api/v1'`
- `stores/auth.ts` — Pinia auth (login/register/logout/init)
- `stores/documents.ts` — Pinia documents CRUD
- `router/index.ts` — vue-router with `requiresAuth` and `guest` meta guards
- `types/index.ts` — all TypeScript interfaces

Routes: `/` (landing) → `/login` `/register` (guest) → `/app/**` (authenticated, AppLayout sidebar) → `/editor/:id` (full-screen CV editor)

## Key Patterns

### Models

- **UUID primary keys** on all models: `id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- **Soft delete** on `Document`: `deleted_at` field, `SoftDeleteManager` (default) + `AllObjectsManager` (admin/DSGVO). `perform_destroy` calls `soft_delete()`, never hard-deletes via API.
- **Timestamps**: `created_at` (auto_now_add) + `updated_at` (auto_now) on every model
- **Document content**: `JSONField` with German-named keys (`persoenliche_daten`, `berufserfahrung`, `ausbildung`, `kenntnisse`, `sprachen`, etc.)

### ViewSets

- Always filter by `request.user`: `Document.objects.filter(user=self.request.user)`
- Two-serializer pattern: `DocumentListSerializer` (lightweight) vs `DocumentDetailSerializer` (full)
- Custom actions: `@action(detail=True, methods=["post"])` for duplicate/preview/ats_score/pdf

### URL Routing

All API endpoints under `/api/v1/`. Apps define `app_name` for namespacing. Admin at `/admin-dashboard/` (not `/admin/`).

### Admin UI (Unfold)

`django-unfold` provides the admin interface. Configured in `base.py` `UNFOLD` dict with German sidebar navigation, environment badge (Entwicklung/Produktion), and sky-blue primary color. Admin classes use `unfold.admin.ModelAdmin`, `@display` decorators for colored status labels, and `unfold.contrib.filters` for dropdown/date-range filters.

## German-Specific Conventions

- **UI strings**: "Anmelden" (login), "Registrieren" (register), "Lebenslauf" (CV), "Bewerbungsschreiben" (cover letter)
- **Model fields**: `anrede`, `geburtsdatum`, `strasse`, `plz`, `stadt`, `bundesland`, `staatsangehoerigkeit`
- **Section types**: `persoenliche_daten`, `berufserfahrung`, `ausbildung`, `kenntnisse`, `sprachen`, `weiterbildungen`, `ehrenamt`, `interessen`, `unterschrift`
- **Template categories**: `klassisch`, `modern`, `kreativ`, `akademisch`, `it_tech`, `student`
- **Timezone**: `Europe/Berlin`, `LANGUAGE_CODE = "de"`
- **All verbose_name strings use gettext_lazy**: `_("Benutzer")`, `_("Dokument")`, etc.

## DSGVO Compliance

- GDPR endpoints: `POST /api/v1/users/me/gdpr/export/` (Art. 20) and `/gdpr/delete/` (Art. 17)
- Consent tracking on `UserProfile`: `privacy_accepted_at`, `marketing_consent`, `newsletter_consent`
- Cookie consent middleware: categories `necessary`/`statistics`/`marketing`/`external_media`
- Documents use soft delete for audit trail
- Password min length: 10 chars. Rate limits: login 5/300s, signup 5/300s, confirm_email 3/180s

## Custom Skills (Plugin: lebenslauf-builder-skills v2.0.0)

This project has 13 custom skills in `lebenslauf-skills-plugin/skills/`. Use the Skill tool to invoke them when the task matches.

| Skill | Invoke when |
|-------|-------------|
| `django-api-core` | Setting up Django project, creating models, configuring settings, Docker, migrations |
| `vue-cv-editor` | Building the CV editor, editor components, live preview, drag-and-drop sections |
| `vue-dashboard` | Building dashboard (Mein Bereich), document management UI, user settings page |
| `german-legal-compliance` | Impressum, cookie consent (TTDSG §25), DSGVO compliance, Datenschutzerklärung |
| `stripe-payment-de` | Stripe checkout, subscriptions, SEPA/Giropay, MwSt 19%, Widerrufsrecht |
| `lebenslauf-templates` | CV template design, HTML/CSS templates, PDF rendering with WeasyPrint |
| `karriere-blog-seo` | Blog system, SEO, structured data (JSON-LD), XML sitemap, Django-rendered pages |
| `n8n-automation-workflows` | n8n workflows, webhooks, Celery tasks, automation orchestration |
| `deployment-hetzner` | Production deployment, Hetzner Cloud, Docker, Nginx, SSL, CI/CD |
| `apify-job-scraper` | Job scraping via Apify, LinkedIn/Indeed/StepStone integration, webhook flow |
| `ai-cover-letter-engine` | AI cover letter generation (Bewerbungsschreiben), Claude API prompts, DIN 5008 |
| `email-automation-de` | Gmail OAuth2, SMTP sending, IMAP response monitoring, anti-spam |
| `application-pipeline` | Application tracking (Kanban), pipeline states, response classification |

Skills are activated via the `lebenslauf-builder-skills` plugin (see `.claude/settings.json`). Each skill's `SKILL.md` contains detailed implementation guidance, architecture decisions, and code patterns.

## Infrastructure

- **PostgreSQL 16** (docker-compose service `db`, database `lebenslauf_db`)
- **Redis 7** — db0: cache, db1: sessions, db2: Celery broker, db3: Celery results
- **Celery task routing**: `payments.*` → queue `payments`, `legal.*` → queue `gdpr`, `automation.send_*` → queue `emails`
- **WeasyPrint** for PDF generation (requires system libs in Docker)
- **Anthropic Claude API** for AI features (model configured via `CLAUDE_MODEL` env var)
- **Stripe** for payments (EUR, SEPA)
- **Brevo CRM** (`sib-api-v3-sdk`) — contact sync on registration via Celery task (`accounts.tasks.sync_brevo_contact_task`). Requires `BREVO_API_KEY` env var.
- **WhiteNoise** for static files, **Hetzner S3** for media (when `USE_S3_STORAGE=true`)
- **Docker image**: Python 3.12-slim (multi-stage build). Local dev may use Python 3.13+ via system/venv.
- **Production**: Gunicorn behind Nginx behind Traefik on Hetzner VPS. Deploy via `docker-compose.prod.yml`.
