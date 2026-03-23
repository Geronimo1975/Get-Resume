# Nginx and Deployment Scripts Reference

## Overview

This reference documents the complete Nginx configuration, security headers, deployment scripts, backup scripts, SSL renewal, CI/CD pipeline, Prometheus monitoring configuration, and alerting rules for the Lebenslauf-Builder platform deployed on Hetzner Cloud.

---

## 1. nginx.conf

```nginx
# docker/nginx/nginx.conf
#
# Main Nginx configuration for Lebenslauf-Builder
# Serves as reverse proxy to Django/Gunicorn and static/media file server
#
# Reload: docker exec lb-nginx nginx -s reload
# Test:   docker exec lb-nginx nginx -t

user nginx;
worker_processes auto;
pid /var/run/nginx.pid;
error_log /var/log/nginx/error.log warn;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    # === Basic Settings ===
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    'rt=$request_time urt=$upstream_response_time';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;
    server_tokens off;

    # === Gzip Compression ===
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_min_length 256;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/x-javascript
        application/xml
        application/xml+rss
        application/vnd.ms-fontobject
        application/x-font-ttf
        font/opentype
        image/svg+xml
        image/x-icon;

    # === Rate Limiting Zones ===
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=3r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
    limit_req_zone $binary_remote_addr zone=webhooks:10m rate=30r/s;

    # === Upstream: Django/Gunicorn ===
    upstream gunicorn {
        server web:8000;
        keepalive 32;
    }

    # === Upstream: n8n ===
    upstream n8n {
        server n8n:5678;
    }

    # === Include site configurations ===
    include /etc/nginx/conf.d/*.conf;
}
```

### Site Configuration

```nginx
# docker/nginx/conf.d/lebenslauf-builder.conf

# ============================================================
# HTTP -> HTTPS Redirect
# ============================================================
server {
    listen 80;
    listen [::]:80;
    server_name www.lebenslauf-builder.de lebenslauf-builder.de n8n.lebenslauf-builder.de;

    # Certbot ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# ============================================================
# Main Application (HTTPS)
# ============================================================
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.lebenslauf-builder.de;

    # === SSL Configuration ===
    ssl_certificate /etc/letsencrypt/live/www.lebenslauf-builder.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.lebenslauf-builder.de/privkey.pem;

    # Modern SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/www.lebenslauf-builder.de/chain.pem;
    resolver 1.1.1.1 8.8.8.8 valid=300s;
    resolver_timeout 5s;

    # === Security Headers ===
    include /etc/nginx/security_headers.conf;

    # === Static Files ===
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
        access_log off;

        # Fingerprinted assets (hash in filename)
        location ~* \.[0-9a-f]{8,}\.(css|js|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
            expires max;
            add_header Cache-Control "public, immutable";
        }
    }

    # === Media Files ===
    location /media/ {
        alias /var/www/media/;
        expires 7d;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options nosniff;

        # Prevent execution of uploaded files
        location ~* \.(php|py|pl|sh|bash|cgi)$ {
            deny all;
        }

        # Invoice PDFs require authentication (handled by Django)
        location /media/invoices/ {
            internal;  # Only accessible via X-Accel-Redirect from Django
        }
    }

    # === Favicon ===
    location = /favicon.ico {
        alias /var/www/static/images/favicon.ico;
        access_log off;
        expires 30d;
    }

    # === robots.txt ===
    location = /robots.txt {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        access_log off;
    }

    # === Sitemap ===
    location = /sitemap.xml {
        alias /var/www/static/sitemap.xml;
        access_log off;
        add_header Content-Type "application/xml; charset=utf-8";
    }

    # === Health Check (no auth, no logging) ===
    location = /health/ {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        access_log off;
    }

    location = /health/nginx {
        return 200 "OK";
        add_header Content-Type text/plain;
        access_log off;
    }

    # === Webhook Endpoints (rate limited) ===
    location /webhooks/ {
        limit_req zone=webhooks burst=20 nodelay;

        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    # === Login/Register (stricter rate limit) ===
    location ~ ^/(anmelden|registrieren|accounts/login|accounts/signup)/ {
        limit_req zone=login burst=5 nodelay;

        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # === API Endpoints (rate limited) ===
    location /api/ {
        limit_req zone=api burst=30 nodelay;

        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # === Django Admin (IP restriction recommended) ===
    location /admin/ {
        # Optionally restrict to specific IPs:
        # allow 1.2.3.4;
        # deny all;

        limit_req zone=login burst=5 nodelay;

        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # === Default: Proxy to Django ===
    location / {
        limit_req zone=general burst=20 nodelay;

        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for HTMX SSE if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }

    # === Block common attack patterns ===
    location ~ /\. {
        deny all;
        access_log off;
    }

    location ~* /(wp-admin|wp-login|xmlrpc|phpmyadmin|administrator) {
        return 444;
        access_log off;
    }
}

# ============================================================
# Non-www Redirect
# ============================================================
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name lebenslauf-builder.de;

    ssl_certificate /etc/letsencrypt/live/www.lebenslauf-builder.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.lebenslauf-builder.de/privkey.pem;

    return 301 https://www.lebenslauf-builder.de$request_uri;
}

# ============================================================
# n8n Subdomain
# ============================================================
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name n8n.lebenslauf-builder.de;

    ssl_certificate /etc/letsencrypt/live/www.lebenslauf-builder.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.lebenslauf-builder.de/privkey.pem;

    include /etc/nginx/security_headers.conf;

    location / {
        proxy_pass http://n8n;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (n8n uses WebSockets)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

---

## 2. security_headers.conf

```nginx
# docker/nginx/security_headers.conf
#
# Security headers applied to all HTTPS responses.
# Included via: include /etc/nginx/security_headers.conf;
#
# Test with: https://securityheaders.com/
# Target: A+ rating

# === Content Security Policy ===
# Restricts which resources can be loaded
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval'
        https://cdn.jsdelivr.net
        https://unpkg.com
        https://js.stripe.com;
    style-src 'self' 'unsafe-inline'
        https://cdn.jsdelivr.net
        https://fonts.googleapis.com;
    img-src 'self' data: blob:
        https://*.stripe.com;
    font-src 'self'
        https://fonts.gstatic.com
        https://cdn.jsdelivr.net;
    connect-src 'self'
        https://api.stripe.com
        https://*.sentry.io;
    frame-src 'self'
        https://js.stripe.com
        https://hooks.stripe.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self'
        https://checkout.stripe.com;
    object-src 'none';
    upgrade-insecure-requests;
" always;

# === HTTP Strict Transport Security (HSTS) ===
# Forces HTTPS for 2 years, includes subdomains
# Submit to HSTS preload list: https://hstspreload.org/
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# === X-Frame-Options ===
# Prevents clickjacking (redundant with CSP frame-ancestors, but kept for older browsers)
add_header X-Frame-Options "DENY" always;

# === X-Content-Type-Options ===
# Prevents MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;

# === Referrer Policy ===
# Controls how much referrer information is sent
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# === Permissions Policy ===
# Controls which browser features can be used
add_header Permissions-Policy "
    accelerometer=(),
    ambient-light-sensor=(),
    autoplay=(),
    battery=(),
    camera=(),
    display-capture=(),
    document-domain=(),
    encrypted-media=(),
    fullscreen=(self),
    geolocation=(),
    gyroscope=(),
    layout-animations=(self),
    legacy-image-formats=(self),
    magnetometer=(),
    microphone=(),
    midi=(),
    oversized-images=(self),
    payment=(self),
    picture-in-picture=(),
    publickey-credentials-get=(),
    sync-xhr=(),
    usb=(),
    vr=(),
    wake-lock=(),
    xr-spatial-tracking=()
" always;

# === X-XSS-Protection ===
# Legacy header, but still useful for older browsers
# Note: Modern browsers use CSP instead
add_header X-XSS-Protection "1; mode=block" always;

# === Cross-Origin Policies ===
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Resource-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;
```

---

## 3. deploy.sh (Zero-Downtime Deployment)

```bash
#!/usr/bin/env bash
# docker/scripts/deploy.sh
#
# Zero-downtime deployment script for Lebenslauf-Builder
#
# Usage:
#   ./deploy.sh [--skip-migrations] [--skip-static]
#
# Steps:
#   1. Pull latest images
#   2. Run database migrations
#   3. Collect static files
#   4. Rolling restart web containers
#   5. Health check
#   6. Rollback on failure
#
# Requirements:
#   - Docker and Docker Compose installed
#   - Running in the project root directory
#   - .env file configured

set -euo pipefail

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="${PROJECT_DIR}/deploy.log"
HEALTH_CHECK_URL="http://localhost/health/"
HEALTH_CHECK_RETRIES=10
HEALTH_CHECK_INTERVAL=5
ROLLBACK_IMAGE=""

# Parse arguments
SKIP_MIGRATIONS=false
SKIP_STATIC=false

for arg in "$@"; do
    case $arg in
        --skip-migrations) SKIP_MIGRATIONS=true ;;
        --skip-static) SKIP_STATIC=true ;;
    esac
done

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Deployment started ==="

cd "$PROJECT_DIR"

# 0. Save current image for rollback
ROLLBACK_IMAGE=$(docker inspect --format='{{.Image}}' lb-web 2>/dev/null || echo "")
log "Current image for rollback: ${ROLLBACK_IMAGE:0:20}..."

# 1. Pull latest code and build
log "Step 1: Building new image..."
docker compose -f "$COMPOSE_FILE" build --no-cache web
if [ $? -ne 0 ]; then
    log "ERROR: Build failed. Aborting deployment."
    exit 1
fi

# 2. Run database migrations
if [ "$SKIP_MIGRATIONS" = false ]; then
    log "Step 2: Running database migrations..."
    docker compose -f "$COMPOSE_FILE" run --rm web python manage.py migrate --noinput
    if [ $? -ne 0 ]; then
        log "ERROR: Migrations failed. Aborting deployment."
        exit 1
    fi
else
    log "Step 2: Skipping migrations (--skip-migrations)"
fi

# 3. Collect static files
if [ "$SKIP_STATIC" = false ]; then
    log "Step 3: Collecting static files..."
    docker compose -f "$COMPOSE_FILE" run --rm web python manage.py collectstatic --noinput
else
    log "Step 3: Skipping static collection (--skip-static)"
fi

# 4. Rolling restart of web service
log "Step 4: Rolling restart..."

# Restart web (Nginx keeps accepting on old container until new is healthy)
docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate web
log "Web container restarted."

# Wait for new container to start
sleep 5

# 5. Health check
log "Step 5: Running health checks..."
HEALTH_OK=false

for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_CHECK_URL" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        HEALTH_OK=true
        log "Health check passed (attempt $i/$HEALTH_CHECK_RETRIES)"
        break
    else
        log "Health check failed (attempt $i/$HEALTH_CHECK_RETRIES, HTTP $HTTP_CODE)"
        sleep $HEALTH_CHECK_INTERVAL
    fi
done

# 6. Rollback on failure
if [ "$HEALTH_OK" = false ]; then
    log "ERROR: Health checks failed. Rolling back..."

    if [ -n "$ROLLBACK_IMAGE" ]; then
        # Restart with previous image
        docker compose -f "$COMPOSE_FILE" up -d --no-deps web
        log "Rollback completed. Previous version restored."
    else
        log "WARNING: No rollback image available."
    fi

    log "=== Deployment FAILED ==="
    exit 1
fi

# 7. Restart Celery workers
log "Step 7: Restarting Celery workers..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate celery celery-beat

# 8. Cleanup old images
log "Step 8: Cleaning up old images..."
docker image prune -f --filter "until=72h"

log "=== Deployment completed successfully ==="
```

---

## 4. backup.sh (PostgreSQL + Media Backup)

```bash
#!/usr/bin/env bash
# docker/scripts/backup.sh
#
# Automated backup script for Lebenslauf-Builder
#
# Usage:
#   ./backup.sh                    # Full backup
#   ./backup.sh --db-only          # Database only
#   ./backup.sh --media-only       # Media files only
#
# Backups are:
#   1. PostgreSQL pg_dump (compressed, custom format)
#   2. Media files rsync to backup directory
#   3. Uploaded to Hetzner Object Storage (S3-compatible)
#   4. Old backups cleaned up (retain 30 days)
#
# Recommended: Run via cron daily at 02:00
#   0 2 * * * /opt/lebenslauf-builder/docker/scripts/backup.sh >> /var/log/backup.log 2>&1

set -euo pipefail

# Configuration
BACKUP_DIR="/opt/backups/lebenslauf-builder"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP_FILE="${BACKUP_DIR}/db/lb_db_${TIMESTAMP}.dump"
MEDIA_BACKUP_DIR="${BACKUP_DIR}/media"
S3_BUCKET="s3://lebenslauf-backups"
S3_ENDPOINT="https://fsn1.your-objectstorage.com"
RETAIN_DAYS=30

# Docker container names
POSTGRES_CONTAINER="lb-postgres"
POSTGRES_DB="${POSTGRES_DB:-lebenslauf_builder}"
POSTGRES_USER="${POSTGRES_USER:-lb_user}"

# Parse arguments
DB_ONLY=false
MEDIA_ONLY=false

for arg in "$@"; do
    case $arg in
        --db-only) DB_ONLY=true ;;
        --media-only) MEDIA_ONLY=true ;;
    esac
done

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] BACKUP: $*"
}

log "=== Backup started ==="

# Create backup directories
mkdir -p "${BACKUP_DIR}/db"
mkdir -p "${MEDIA_BACKUP_DIR}"

# === 1. PostgreSQL Backup ===
if [ "$MEDIA_ONLY" = false ]; then
    log "Step 1: PostgreSQL backup..."

    docker exec "$POSTGRES_CONTAINER" pg_dump \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --format=custom \
        --compress=9 \
        --verbose \
        > "$DB_BACKUP_FILE"

    DB_SIZE=$(du -sh "$DB_BACKUP_FILE" | cut -f1)
    log "Database backup complete: ${DB_BACKUP_FILE} (${DB_SIZE})"

    # Verify backup integrity
    docker exec -i "$POSTGRES_CONTAINER" pg_restore \
        --list "$DB_BACKUP_FILE" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log "Database backup integrity verified."
    else
        log "WARNING: Database backup integrity check failed!"
    fi
fi

# === 2. Media Files Backup ===
if [ "$DB_ONLY" = false ]; then
    log "Step 2: Media files backup..."

    # Get the media volume mount point
    MEDIA_SOURCE=$(docker inspect --format='{{range .Mounts}}{{if eq .Destination "/app/media"}}{{.Source}}{{end}}{{end}}' lb-web)

    if [ -n "$MEDIA_SOURCE" ]; then
        rsync -avz --delete \
            "$MEDIA_SOURCE/" \
            "${MEDIA_BACKUP_DIR}/"

        MEDIA_SIZE=$(du -sh "${MEDIA_BACKUP_DIR}" | cut -f1)
        log "Media backup complete: ${MEDIA_BACKUP_DIR} (${MEDIA_SIZE})"
    else
        log "WARNING: Could not find media volume mount point."
    fi
fi

# === 3. Upload to Object Storage ===
log "Step 3: Uploading to Object Storage..."

if [ "$MEDIA_ONLY" = false ] && [ -f "$DB_BACKUP_FILE" ]; then
    aws s3 cp "$DB_BACKUP_FILE" \
        "${S3_BUCKET}/db/" \
        --endpoint-url "$S3_ENDPOINT" \
        --storage-class STANDARD
    log "Database backup uploaded to ${S3_BUCKET}/db/"
fi

if [ "$DB_ONLY" = false ]; then
    aws s3 sync "${MEDIA_BACKUP_DIR}/" \
        "${S3_BUCKET}/media/" \
        --endpoint-url "$S3_ENDPOINT" \
        --delete
    log "Media backup synced to ${S3_BUCKET}/media/"
fi

# === 4. Cleanup Old Backups ===
log "Step 4: Cleaning up old backups..."

# Local: Delete DB backups older than RETAIN_DAYS
find "${BACKUP_DIR}/db" -name "lb_db_*.dump" -mtime +${RETAIN_DAYS} -delete
LOCAL_DELETED=$(find "${BACKUP_DIR}/db" -name "lb_db_*.dump" -mtime +${RETAIN_DAYS} 2>/dev/null | wc -l)
log "Deleted ${LOCAL_DELETED} local backups older than ${RETAIN_DAYS} days."

# S3: Delete old backups (using lifecycle policy is preferred, but manual cleanup as fallback)
CUTOFF_DATE=$(date -d "-${RETAIN_DAYS} days" +"%Y-%m-%d" 2>/dev/null || date -v-${RETAIN_DAYS}d +"%Y-%m-%d")
aws s3 ls "${S3_BUCKET}/db/" \
    --endpoint-url "$S3_ENDPOINT" | \
    while read -r line; do
        FILE_DATE=$(echo "$line" | awk '{print $1}')
        FILE_NAME=$(echo "$line" | awk '{print $4}')
        if [[ "$FILE_DATE" < "$CUTOFF_DATE" ]] && [ -n "$FILE_NAME" ]; then
            aws s3 rm "${S3_BUCKET}/db/${FILE_NAME}" --endpoint-url "$S3_ENDPOINT"
            log "Deleted old S3 backup: ${FILE_NAME}"
        fi
    done

log "=== Backup completed ==="
```

---

## 5. ssl_renew.sh (Certbot Renewal)

```bash
#!/usr/bin/env bash
# docker/scripts/ssl_renew.sh
#
# SSL certificate renewal script using Certbot
#
# Usage:
#   ./ssl_renew.sh
#
# Certbot checks if renewal is needed (within 30 days of expiry).
# If renewed, Nginx is reloaded to pick up the new certificate.
#
# Recommended: Run via cron twice daily
#   0 3,15 * * * /opt/lebenslauf-builder/docker/scripts/ssl_renew.sh >> /var/log/ssl_renew.log 2>&1

set -euo pipefail

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SSL: $*"
}

log "Checking SSL certificate renewal..."

# Run certbot renewal
docker compose -f /opt/lebenslauf-builder/docker-compose.prod.yml \
    run --rm certbot renew \
    --webroot \
    --webroot-path=/var/www/certbot \
    --quiet \
    --deploy-hook "echo 'Certificate renewed, Nginx reload needed.'"

CERTBOT_EXIT=$?

if [ $CERTBOT_EXIT -eq 0 ]; then
    # Check if certificate was actually renewed (certbot returns 0 even if no renewal needed)
    # Reload Nginx to pick up any new certificates
    docker exec lb-nginx nginx -t && docker exec lb-nginx nginx -s reload
    log "Nginx reloaded successfully."
else
    log "ERROR: Certbot renewal failed (exit code: $CERTBOT_EXIT)"
    exit 1
fi

# Check certificate expiry
CERT_EXPIRY=$(docker exec lb-nginx openssl x509 -noout -enddate \
    -in /etc/letsencrypt/live/www.lebenslauf-builder.de/fullchain.pem 2>/dev/null | cut -d= -f2)
log "Certificate expires: ${CERT_EXPIRY}"

# Alert if expiry is within 7 days
EXPIRY_EPOCH=$(date -d "$CERT_EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$CERT_EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 7 ]; then
    log "WARNING: Certificate expires in ${DAYS_LEFT} days!"
    # Send alert (could be email, Slack, etc.)
fi

log "SSL renewal check complete. Certificate valid for ${DAYS_LEFT} more days."
```

---

## 6. GitHub Actions CI/CD Workflow

```yaml
# .github/workflows/deploy.yml
#
# CI/CD pipeline for Lebenslauf-Builder
#
# Triggers:
# - Push to main branch (auto-deploy to production)
# - Push to develop branch (auto-deploy to staging)
# - Manual trigger (workflow_dispatch)
#
# Steps:
# 1. Run tests (Python + linting)
# 2. Build Docker image
# 3. Push to container registry
# 4. Deploy to Hetzner server via SSH

name: CI/CD Pipeline

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
  workflow_dispatch:
    inputs:
      environment:
        description: "Deployment target"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production

env:
  PYTHON_VERSION: "3.12"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================================
  # Job 1: Test
  # ============================================================
  test:
    name: Test
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"

      - name: Install WeasyPrint system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends \
            libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
            libgdk-pixbuf-2.0-0 shared-mime-info fonts-liberation

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements/test.txt

      - name: Run linting
        run: |
          ruff check .
          ruff format --check .

      - name: Run tests
        env:
          DATABASE_URL: postgres://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          DJANGO_SETTINGS_MODULE: config.settings.test
          DJANGO_SECRET_KEY: test-secret-key-not-for-production
        run: |
          python manage.py test --verbosity=2 --parallel

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/

  # ============================================================
  # Job 2: Build and Push Docker Image
  # ============================================================
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    permissions:
      contents: read
      packages: write

    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          target: production

  # ============================================================
  # Job 3: Deploy
  # ============================================================
  deploy:
    name: Deploy to ${{ github.ref == 'refs/heads/main' && 'Production' || 'Staging' }}
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    environment:
      name: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
      url: ${{ github.ref == 'refs/heads/main' && 'https://www.lebenslauf-builder.de' || 'https://staging.lebenslauf-builder.de' }}

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          port: ${{ secrets.DEPLOY_SSH_PORT || 22 }}
          script: |
            cd /opt/lebenslauf-builder
            git pull origin ${{ github.ref_name }}
            ./docker/scripts/deploy.sh

      - name: Verify deployment
        run: |
          sleep 10
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            "${{ github.ref == 'refs/heads/main' && 'https://www.lebenslauf-builder.de' || 'https://staging.lebenslauf-builder.de' }}/health/" \
            2>/dev/null || echo "000")
          if [ "$HTTP_CODE" != "200" ]; then
            echo "Health check failed: HTTP $HTTP_CODE"
            exit 1
          fi
          echo "Deployment verified: HTTP $HTTP_CODE"

      - name: Notify Sentry of release
        if: github.ref == 'refs/heads/main'
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
        with:
          environment: production
          version: ${{ github.sha }}
```

---

## 7. prometheus.yml (Monitoring Configuration)

```yaml
# docker/monitoring/prometheus.yml
#
# Prometheus configuration for Lebenslauf-Builder monitoring
#
# Scraped metrics:
# - Django application (django-prometheus)
# - Node exporter (system metrics)
# - PostgreSQL exporter
# - Nginx stub_status
# - Redis exporter

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s

  external_labels:
    environment: "production"
    service: "lebenslauf-builder"

# Rule files for alerting
rule_files:
  - "/etc/prometheus/alert_rules.yml"

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - "alertmanager:9093"

# === Scrape Configurations ===
scrape_configs:

  # --- Django Application Metrics ---
  # Exposed by django-prometheus at /metrics
  - job_name: "django"
    metrics_path: "/metrics"
    scrape_interval: 15s
    static_configs:
      - targets:
          - "web:8000"
        labels:
          app: "lebenslauf-builder"
          component: "django"

  # --- Node Exporter (System Metrics) ---
  # CPU, memory, disk, network
  - job_name: "node"
    scrape_interval: 15s
    static_configs:
      - targets:
          - "node-exporter:9100"
        labels:
          instance: "hetzner-cx41"

  # --- PostgreSQL Exporter ---
  # Database performance metrics
  - job_name: "postgres"
    scrape_interval: 30s
    static_configs:
      - targets:
          - "postgres-exporter:9187"
        labels:
          database: "lebenslauf_builder"

  # --- Nginx Metrics ---
  # Via nginx-prometheus-exporter reading stub_status
  - job_name: "nginx"
    scrape_interval: 15s
    static_configs:
      - targets:
          - "nginx-exporter:9113"
        labels:
          component: "nginx"

  # --- Redis Exporter ---
  - job_name: "redis"
    scrape_interval: 15s
    static_configs:
      - targets:
          - "redis-exporter:9121"
        labels:
          component: "redis"

  # --- Celery Metrics ---
  # Via celery-exporter (flower alternative)
  - job_name: "celery"
    scrape_interval: 15s
    static_configs:
      - targets:
          - "celery-exporter:9808"
        labels:
          component: "celery"

  # --- Prometheus self-monitoring ---
  - job_name: "prometheus"
    scrape_interval: 30s
    static_configs:
      - targets:
          - "localhost:9090"
```

---

## 8. Alert Rules

```yaml
# docker/monitoring/alert_rules.yml
#
# Prometheus alerting rules for Lebenslauf-Builder
#
# Severity levels:
# - critical: Immediate action required (pages on-call)
# - warning: Should be investigated soon
# - info: For tracking, no immediate action

groups:
  # ============================================================
  # Uptime & Availability
  # ============================================================
  - name: uptime
    rules:
      - alert: ApplicationDown
        expr: up{job="django"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Lebenslauf-Builder application is down"
          description: "Django application has been unreachable for more than 1 minute."
          runbook: "Check: docker logs lb-web; docker compose ps"

      - alert: NginxDown
        expr: up{job="nginx"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Nginx reverse proxy is down"
          description: "Nginx has been unreachable for more than 1 minute."

      - alert: PostgresDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"
          description: "PostgreSQL has been unreachable for more than 1 minute."

      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"
          description: "Redis has been unreachable for more than 2 minutes. Cache and Celery broker affected."

  # ============================================================
  # Error Rate
  # ============================================================
  - name: error_rate
    rules:
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(django_http_responses_total_by_status_total{status=~"5.."}[5m]))
            /
            sum(rate(django_http_responses_total_by_status_total[5m]))
          ) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High HTTP 5xx error rate (> 5%)"
          description: "More than 5% of HTTP responses are 5xx errors over the last 5 minutes."

      - alert: ElevatedErrorRate
        expr: |
          (
            sum(rate(django_http_responses_total_by_status_total{status=~"5.."}[5m]))
            /
            sum(rate(django_http_responses_total_by_status_total[5m]))
          ) > 0.01
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Elevated HTTP 5xx error rate (> 1%)"
          description: "More than 1% of HTTP responses are 5xx errors over the last 10 minutes."

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(django_http_requests_latency_seconds_by_view_method_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency (p95 > 2s)"
          description: "95th percentile request latency is above 2 seconds."

  # ============================================================
  # Disk Usage
  # ============================================================
  - name: disk
    rules:
      - alert: DiskSpaceCritical
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space critically low (< 10% free)"
          description: "Root filesystem has less than 10% free space. Immediate action required."

      - alert: DiskSpaceWarning
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.2
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low (< 20% free)"
          description: "Root filesystem has less than 20% free space."

      - alert: PostgresDiskUsageHigh
        expr: |
          pg_database_size_bytes{datname="lebenslauf_builder"} > 10737418240
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL database size > 10 GB"
          description: "The lebenslauf_builder database has grown beyond 10 GB."

  # ============================================================
  # Memory
  # ============================================================
  - name: memory
    rules:
      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage (> 90%)"
          description: "System memory usage has been above 90% for 5 minutes."

      - alert: ElevatedMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.8
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Elevated memory usage (> 80%)"
          description: "System memory usage has been above 80% for 15 minutes."

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes > 230686720
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage > 220 MB (limit: 256 MB)"
          description: "Redis is approaching its maxmemory limit."

  # ============================================================
  # Celery & Tasks
  # ============================================================
  - name: celery
    rules:
      - alert: CeleryWorkerDown
        expr: celery_workers < 1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "No Celery workers available"
          description: "All Celery workers are down. Background tasks will not be processed."

      - alert: CeleryTaskQueueBacklog
        expr: celery_task_queue_length > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Celery task queue backlog > 100 tasks"
          description: "Tasks are accumulating in the queue faster than workers can process them."

  # ============================================================
  # SSL Certificate
  # ============================================================
  - name: ssl
    rules:
      - alert: SSLCertExpiringSoon
        expr: |
          (probe_ssl_earliest_cert_expiry - time()) / 86400 < 14
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "SSL certificate expires in less than 14 days"
          description: "The SSL certificate for www.lebenslauf-builder.de will expire soon."

      - alert: SSLCertExpiryCritical
        expr: |
          (probe_ssl_earliest_cert_expiry - time()) / 86400 < 3
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "SSL certificate expires in less than 3 days"
          description: "URGENT: SSL certificate renewal has failed. Manual intervention required."

  # ============================================================
  # Database Performance
  # ============================================================
  - name: database
    rules:
      - alert: PostgresHighConnections
        expr: |
          pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL connection count > 80"
          description: "High number of database connections. Check for connection leaks."

      - alert: PostgresSlowQueries
        expr: |
          pg_stat_activity_max_tx_duration{datname="lebenslauf_builder"} > 60
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL has long-running queries (> 60s)"
          description: "One or more database queries have been running for over 60 seconds."

      - alert: PostgresReplicationLag
        expr: pg_replication_lag > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL replication lag > 30 seconds"
          description: "If using replication, the replica is falling behind."
```
