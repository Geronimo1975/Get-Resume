# Docker Configuration Reference

## Overview

This reference documents the complete Docker configuration for the Lebenslauf-Builder platform deployment on Hetzner Cloud. It includes the application Dockerfile (multi-stage build), n8n Dockerfile, docker-compose production configuration, environment variables, volume management, and networking.

---

## 1. Dockerfile (Multi-Stage Build)

```dockerfile
# Dockerfile
# Multi-stage build for the Lebenslauf-Builder Django application
#
# Stage 1 (builder): Install Python dependencies, compile assets
# Stage 2 (production): Minimal runtime image with gunicorn
#
# Build: docker build -t lebenslauf-builder:latest .
# Run:   docker run -p 8000:8000 --env-file .env lebenslauf-builder:latest

# ============================================================
# Stage 1: Builder
# ============================================================
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install Python dependencies
COPY requirements/production.txt /app/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Production
# ============================================================
FROM python:3.12-slim AS production

# Labels
LABEL maintainer="Lebenslauf-Builder GmbH <dev@lebenslauf-builder.de>"
LABEL description="Lebenslauf-Builder Django Application"
LABEL version="1.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=8000

# === Install runtime dependencies ===
# WeasyPrint requires: pango, cairo, gdk-pixbuf, fontconfig, shared-mime-info
# PostgreSQL client for pg_isready health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libcairo-gobject2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libglib2.0-0 \
    # Font packages for PDF rendering
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-core \
    fonts-noto-cjk \
    fontconfig \
    # PostgreSQL client
    libpq5 \
    postgresql-client \
    # curl for health checks
    curl \
    # mime-support for proper file type detection
    mime-support \
    && rm -rf /var/lib/apt/lists/* \
    # Rebuild font cache
    && fc-cache -f -v

# Copy Python packages from builder stage
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Create required directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R appuser:appuser /app

# Copy application code
WORKDIR /app
COPY --chown=appuser:appuser . /app/

# Collect static files (runs with dummy secret key)
RUN DJANGO_SECRET_KEY=dummy-key-for-collectstatic \
    DATABASE_URL=sqlite:///tmp/dummy.db \
    python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Switch to non-root user
USER appuser

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health/ || exit 1

# Run gunicorn
CMD ["gunicorn", \
     "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--worker-tmp-dir", "/dev/shm", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
```

---

## 2. Dockerfile.n8n

```dockerfile
# Dockerfile.n8n
# Custom n8n image with additional nodes and configuration
#
# Based on the official n8n image with:
# - PostgreSQL support (n8n database)
# - Custom environment defaults
# - Health check

FROM docker.n8n.io/n8nio/n8n:latest

# Labels
LABEL maintainer="Lebenslauf-Builder GmbH"
LABEL description="n8n automation for Lebenslauf-Builder"

# Environment defaults (can be overridden in docker-compose)
ENV N8N_PORT=5678 \
    N8N_PROTOCOL=https \
    N8N_HOST=n8n.lebenslauf-builder.de \
    N8N_EDITOR_BASE_URL=https://n8n.lebenslauf-builder.de/ \
    WEBHOOK_URL=https://n8n.lebenslauf-builder.de/ \
    N8N_LOG_LEVEL=info \
    N8N_METRICS=true \
    N8N_DIAGNOSTICS_ENABLED=false \
    N8N_PERSONALIZATION_ENABLED=false \
    EXECUTIONS_DATA_PRUNE=true \
    EXECUTIONS_DATA_MAX_AGE=168 \
    GENERIC_TIMEZONE=Europe/Berlin

# Data directory for n8n workflows and credentials
VOLUME ["/home/node/.n8n"]

# Expose n8n port
EXPOSE 5678

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -q --spider http://localhost:5678/healthz || exit 1
```

---

## 3. docker-compose.prod.yml

```yaml
# docker-compose.prod.yml
#
# Production Docker Compose for Lebenslauf-Builder
#
# Usage:
#   docker compose -f docker-compose.prod.yml up -d
#   docker compose -f docker-compose.prod.yml logs -f web
#
# Services:
#   - web:          Django + Gunicorn (application server)
#   - celery:       Celery worker (task processing)
#   - celery-beat:  Celery beat (periodic task scheduler)
#   - postgres:     PostgreSQL 16 (primary database)
#   - redis:        Redis 7 (cache + Celery broker)
#   - nginx:        Nginx (reverse proxy + static files)
#   - n8n:          n8n (automation workflows)

version: "3.8"

services:
  # ============================================================
  # Django Application Server
  # ============================================================
  web:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: lebenslauf-builder:latest
    container_name: lb-web
    restart: unless-stopped
    env_file: .env
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    volumes:
      - media_data:/app/media
      - static_data:/app/staticfiles
      - app_logs:/app/logs
    networks:
      - internal
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M

  # ============================================================
  # Celery Worker
  # ============================================================
  celery:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: lebenslauf-builder:latest
    container_name: lb-celery
    restart: unless-stopped
    env_file: .env
    command: >
      celery -A config worker
      --loglevel=info
      --queues=default,pdf,email,gdpr
      --concurrency=4
      --max-tasks-per-child=100
      --without-heartbeat
    volumes:
      - media_data:/app/media
      - app_logs:/app/logs
    networks:
      - internal
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "celery", "-A", "config", "inspect", "ping", "--timeout", "10"]
      interval: 60s
      timeout: 15s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 1G
        reservations:
          cpus: "0.25"
          memory: 256M

  # ============================================================
  # Celery Beat (Periodic Task Scheduler)
  # ============================================================
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: lebenslauf-builder:latest
    container_name: lb-celery-beat
    restart: unless-stopped
    env_file: .env
    command: >
      celery -A config beat
      --loglevel=info
      --scheduler=django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - app_logs:/app/logs
    networks:
      - internal
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M

  # ============================================================
  # PostgreSQL Database
  # ============================================================
  postgres:
    image: postgres:16-alpine
    container_name: lb-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-lebenslauf_builder}
      POSTGRES_USER: ${POSTGRES_USER:-lb_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=de_DE.UTF-8 --lc-ctype=de_DE.UTF-8"
      # Performance tuning
      POSTGRES_SHARED_BUFFERS: "256MB"
      POSTGRES_EFFECTIVE_CACHE_SIZE: "768MB"
      POSTGRES_WORK_MEM: "16MB"
      POSTGRES_MAINTENANCE_WORK_MEM: "128MB"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-lb_user} -d ${POSTGRES_DB:-lebenslauf_builder}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M

  # ============================================================
  # Redis (Cache + Celery Broker)
  # ============================================================
  redis:
    image: redis:7-alpine
    container_name: lb-redis
    restart: unless-stopped
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - internal
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M

  # ============================================================
  # Nginx (Reverse Proxy)
  # ============================================================
  nginx:
    image: nginx:1.25-alpine
    container_name: lb-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/conf.d/:/etc/nginx/conf.d/:ro
      - ./docker/nginx/security_headers.conf:/etc/nginx/security_headers.conf:ro
      - static_data:/var/www/static:ro
      - media_data:/var/www/media:ro
      - certbot_conf:/etc/letsencrypt:ro
      - certbot_www:/var/www/certbot:ro
      - nginx_logs:/var/log/nginx
    networks:
      - internal
    depends_on:
      web:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health/nginx"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 256M

  # ============================================================
  # n8n (Automation Workflows)
  # ============================================================
  n8n:
    build:
      context: .
      dockerfile: Dockerfile.n8n
    container_name: lb-n8n
    restart: unless-stopped
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${N8N_DB_NAME:-n8n}
      - DB_POSTGRESDB_USER=${POSTGRES_USER:-lb_user}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://n8n.lebenslauf-builder.de/
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - internal
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M

  # ============================================================
  # Certbot (SSL Certificate Management)
  # ============================================================
  certbot:
    image: certbot/certbot:latest
    container_name: lb-certbot
    volumes:
      - certbot_conf:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - internal

# ============================================================
# Volumes
# ============================================================
volumes:
  postgres_data:
    driver: local
    name: lb_postgres_data

  redis_data:
    driver: local
    name: lb_redis_data

  media_data:
    driver: local
    name: lb_media_data

  static_data:
    driver: local
    name: lb_static_data

  n8n_data:
    driver: local
    name: lb_n8n_data

  certbot_conf:
    driver: local
    name: lb_certbot_conf

  certbot_www:
    driver: local
    name: lb_certbot_www

  app_logs:
    driver: local
    name: lb_app_logs

  nginx_logs:
    driver: local
    name: lb_nginx_logs

# ============================================================
# Networks
# ============================================================
networks:
  internal:
    driver: bridge
    name: lb_internal
    # Only nginx exposes ports to the host.
    # All other services communicate only on the internal network.
```

---

## 4. .env.example

```bash
# .env.example
#
# Copy to .env and fill in all values:
#   cp .env.example .env
#
# IMPORTANT: Never commit .env to version control!
# The .env file contains secrets and must remain private.

# ============================================================
# Django Core
# ============================================================

# Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=your-secret-key-here-change-this

# Debug mode (NEVER true in production)
DJANGO_DEBUG=false

# Comma-separated list of allowed hosts
DJANGO_ALLOWED_HOSTS=www.lebenslauf-builder.de,lebenslauf-builder.de

# Full site URL (no trailing slash)
SITE_URL=https://www.lebenslauf-builder.de

# Environment identifier
ENVIRONMENT=production

# ============================================================
# Database (PostgreSQL)
# ============================================================

# Django DATABASE_URL format
DATABASE_URL=postgres://lb_user:your-db-password@postgres:5432/lebenslauf_builder

# Individual PostgreSQL settings (used by docker-compose)
POSTGRES_DB=lebenslauf_builder
POSTGRES_USER=lb_user
POSTGRES_PASSWORD=your-db-password

# n8n database (separate from main app)
N8N_DB_NAME=n8n

# ============================================================
# Redis
# ============================================================

REDIS_URL=redis://:your-redis-password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# Celery-specific Redis URLs (different DBs)
CELERY_BROKER_URL=redis://:your-redis-password@redis:6379/1
CELERY_RESULT_BACKEND=redis://:your-redis-password@redis:6379/2

# ============================================================
# Stripe (Payment Processing)
# ============================================================

# Publishable key (safe for frontend)
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Secret key (server-side only)
STRIPE_SECRET_KEY=sk_live_...

# Webhook signing secret (from Stripe Dashboard -> Webhooks)
STRIPE_WEBHOOK_SECRET=whsec_...

# ============================================================
# Email (AWS SES via django-anymail)
# ============================================================

# AWS credentials for SES
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-aws-secret

# SES region
AWS_SES_REGION_NAME=eu-central-1
AWS_SES_REGION_ENDPOINT=email.eu-central-1.amazonaws.com

# Default sender
DEFAULT_FROM_EMAIL=noreply@lebenslauf-builder.de
INVOICE_REPLY_TO_EMAIL=rechnung@lebenslauf-builder.de
SERVER_EMAIL=admin@lebenslauf-builder.de

# ============================================================
# Object Storage (Hetzner / S3-compatible)
# ============================================================

# For media file storage (user uploads, PDFs, invoices)
AWS_S3_ENDPOINT_URL=https://fsn1.your-objectstorage.com
AWS_STORAGE_BUCKET_NAME=lebenslauf-media
AWS_S3_ACCESS_KEY_ID=your-s3-access-key
AWS_S3_SECRET_ACCESS_KEY=your-s3-secret-key
AWS_S3_REGION_NAME=fsn1

# ============================================================
# Sentry (Error Monitoring)
# ============================================================

SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# ============================================================
# n8n (Automation)
# ============================================================

# n8n basic auth (for the n8n web UI)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-n8n-password

# n8n encryption key for stored credentials
# Generate with: openssl rand -hex 32
N8N_ENCRYPTION_KEY=your-n8n-encryption-key

# ============================================================
# Webhook Secrets
# ============================================================

# Internal webhook HMAC secret (Django <-> n8n)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
INTERNAL_WEBHOOK_SECRET=your-internal-webhook-secret
N8N_WEBHOOK_SECRET=your-n8n-webhook-secret

# n8n webhook URLs
N8N_WEBHOOK_USER_REGISTERED=https://n8n.lebenslauf-builder.de/webhook/user-registered
N8N_WEBHOOK_DOCUMENT_CREATED=https://n8n.lebenslauf-builder.de/webhook/document-created
N8N_WEBHOOK_PAYMENT_SUCCEEDED=https://n8n.lebenslauf-builder.de/webhook/payment-succeeded
N8N_WEBHOOK_SUBSCRIPTION_CANCELLED=https://n8n.lebenslauf-builder.de/webhook/subscription-cancelled
N8N_WEBHOOK_GDPR_DELETION=https://n8n.lebenslauf-builder.de/webhook/gdpr-deletion
N8N_WEBHOOK_GDPR_EXPORT=https://n8n.lebenslauf-builder.de/webhook/gdpr-export

# ============================================================
# Security
# ============================================================

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS=https://www.lebenslauf-builder.de,https://lebenslauf-builder.de

# Session cookie settings
SESSION_COOKIE_AGE=1209600
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# ============================================================
# Monitoring
# ============================================================

# Prometheus metrics (optional)
PROMETHEUS_METRICS_ENABLED=true
```

---

## 5. Docker Volumes

| Volume | Container(s) | Mount Path | Purpose |
|--------|-------------|------------|---------|
| `postgres_data` | postgres | `/var/lib/postgresql/data` | PostgreSQL database files |
| `redis_data` | redis | `/data` | Redis AOF persistence |
| `media_data` | web, celery, nginx | `/app/media`, `/var/www/media` | User uploads, PDFs, invoices |
| `static_data` | web, nginx | `/app/staticfiles`, `/var/www/static` | Django collected static files |
| `n8n_data` | n8n | `/home/node/.n8n` | n8n workflows, credentials |
| `certbot_conf` | nginx, certbot | `/etc/letsencrypt` | SSL certificates |
| `certbot_www` | nginx, certbot | `/var/www/certbot` | ACME challenge files |
| `app_logs` | web, celery, celery-beat | `/app/logs` | Application log files |
| `nginx_logs` | nginx | `/var/log/nginx` | Nginx access and error logs |

### Backup Priority

1. **Critical**: `postgres_data` (database), `media_data` (user files)
2. **Important**: `n8n_data` (automation workflows), `certbot_conf` (SSL certs)
3. **Regenerable**: `static_data` (rebuilt from code), `redis_data` (cache)

---

## 6. Docker Networking

```
                    Internet
                       |
                       v
              +--------+--------+
              |                 |
              |  Nginx (:80,:443)|
              |                 |
              +--------+--------+
                       |
            lb_internal network
          (bridge, no external access)
                       |
         +------+------+------+------+
         |      |      |      |      |
         v      v      v      v      v
       Web   Celery  Beat  Postgres  Redis   n8n
      :8000           beat  :5432   :6379  :5678
```

### Network Rules

- **Only Nginx exposes ports** to the host (80 and 443)
- All other services communicate exclusively on the `lb_internal` bridge network
- PostgreSQL is only accessible from the internal network (no port binding to host)
- Redis requires password authentication even on the internal network
- n8n is accessed via Nginx reverse proxy (n8n.lebenslauf-builder.de)

### Service Discovery

Docker Compose automatically creates DNS entries for each service name on the internal network:
- `postgres` resolves to the PostgreSQL container IP
- `redis` resolves to the Redis container IP
- `web` resolves to the Django application container IP
- `n8n` resolves to the n8n container IP

This is why `DATABASE_URL` uses `postgres` as the hostname, not `localhost` or an IP address.
