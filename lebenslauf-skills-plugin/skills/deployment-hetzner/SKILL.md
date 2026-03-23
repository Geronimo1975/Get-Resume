---
name: deployment-hetzner
description: >
  This skill should be used when the user asks to "deploy to production", "set up the server",
  "configure Docker", "set up Nginx", "configure SSL", "implement CI/CD",
  "set up monitoring", "configure backups", "create Dockerfile",
  or mentions deployment, Hetzner, Docker, Nginx, SSL, CI/CD, production, server setup,
  monitoring, Let's Encrypt, reverse proxy, backup, scaling, Prometheus, Sentry,
  zero-downtime deploy, or any infrastructure/deployment task.
---

# Deployment on Hetzner Cloud

Complete production deployment for the GetResume Vue.js SPA + Django API stack with Docker, Nginx, SSL, CI/CD, monitoring, and backups.

## Plugin Settings (Read First)

Before running any deployment command, check for project-specific settings:

```
File: .claude/lebenslauf-builder-skills.local.md
```

Parse the YAML frontmatter to read deployment-specific values:

| Setting | Purpose | Default |
|---------|---------|---------|
| `deploy_host` | Server IP or hostname | `85.215.69.83` |
| `deploy_user` | SSH username | `resume` |
| `ssh_key` | Path to SSH private key | `~/.ssh/resume` |
| `compose_file` | Production compose file | `docker-compose.prod.yml` |
| `domain` | Production domain | `resume.get-hub.io` |
| `sentry_configured` | Whether to notify Sentry on deploy | `false` |
| `n8n_configured` | Whether n8n service is in the stack | `false` |

**Always use these values instead of hardcoded defaults.** If the file doesn't exist, fall back to the defaults above.

### Reading settings in commands

```bash
SETTINGS=".claude/lebenslauf-builder-skills.local.md"
if [[ -f "$SETTINGS" ]]; then
  FM=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SETTINGS")
  HOST=$(echo "$FM" | grep '^deploy_host:' | sed 's/deploy_host: *//' | sed 's/^"\(.*\)"$/\1/')
  USER=$(echo "$FM" | grep '^deploy_user:' | sed 's/deploy_user: *//' | sed 's/^"\(.*\)"$/\1/')
  KEY=$(echo "$FM" | grep '^ssh_key:' | sed 's/ssh_key: *//' | sed 's/^"\(.*\)"$/\1/')
  COMPOSE=$(echo "$FM" | grep '^compose_file:' | sed 's/compose_file: *//' | sed 's/^"\(.*\)"$/\1/')
  DOMAIN=$(echo "$FM" | grep '^domain:' | sed 's/domain: *//' | sed 's/^"\(.*\)"$/\1/')
else
  HOST="85.215.69.83"; USER="resume"; KEY="~/.ssh/resume"
  COMPOSE="docker-compose.prod.yml"; DOMAIN="resume.get-hub.io"
fi
```

Use `$HOST`, `$USER`, `$KEY`, `$COMPOSE`, `$DOMAIN` in all SSH, rsync, and docker commands below.

## Architecture Note

This is a **Vue.js SPA + Django API** deployment:
- Nginx serves the Vue.js SPA build (static files) for all frontend routes
- Nginx proxies `/api/*` and `/admin/*` to Django/Gunicorn
- Vue.js SPA uses client-side routing (Vue Router history mode)
- Nginx must return `index.html` for all non-API routes (SPA fallback)

## Production Stack

```
┌─────────────────────────────────────────┐
│  Hetzner Cloud VPS (CX31/CX41)          │
│  Ubuntu 22.04, Falkenstein (DE/DSGVO)   │
│                                         │
│  ┌─── Nginx (port 80/443) ───┐          │
│  │  SSL termination           │          │
│  │  Security headers          │          │
│  │  /api/* → Django           │          │
│  │  /* → Vue.js SPA (static)  │          │
│  └────────┬──────────────────┘          │
│           ↓                              │
│  ┌─── Docker Compose ────────┐          │
│  │  web: Django + Gunicorn   │          │
│  │  db: PostgreSQL 16        │          │
│  │  redis: Redis 7           │          │
│  │  celery_worker: Celery    │          │
│  │  celery_beat: Scheduler   │          │
│  │  n8n: Workflow engine     │          │
│  └───────────────────────────┘          │
│                                         │
│  /var/www/frontend/ ← Vue.js build      │
│  Prometheus + Sentry (monitoring)       │
└─────────────────────────────────────────┘
```

## Nginx SPA Configuration (Key Difference)

```nginx
server {
    # ... SSL config ...

    # Vue.js SPA — serve static build
    root /var/www/frontend/dist;
    index index.html;

    # API proxy to Django
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        # ... proxy headers ...
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # Django static/media files
    location /static/ {
        alias /var/www/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/backend/media/;
    }

    # Blog (Django-rendered for SEO)
    location /karriere-blog/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # SPA fallback — all other routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## CI/CD Pipeline (GitHub Actions)

```
Push to main →
  1. Run Django tests (pytest)
  2. Run Vue.js tests (Vitest)
  3. Lint (ruff + eslint)
  4. Build Vue.js SPA: npm run build
  5. Build Django Docker image
  6. Push Docker image to GitHub Container Registry
  7. SSH to Hetzner:
     a. docker compose pull (Django)
     b. rsync Vue.js dist/ to /var/www/frontend/dist/
     c. docker compose up -d --no-deps web
     d. python manage.py migrate
     e. python manage.py collectstatic --noinput
  8. Health check
  9. Notify Sentry of release
```

## Server Selection

- **CX31** (4 vCPU, 8GB RAM, 80GB SSD) — MVP
- **CX41** (8 vCPU, 16GB RAM, 160GB SSD) — growth
- Datacenter: Falkenstein or Nuremberg (Germany, DSGVO-compliant)

## Backup Strategy

- PostgreSQL: `pg_dump` daily at 02:00 → Hetzner Object Storage
- Media files: `rsync` daily at 03:00
- 30-day retention

## Monitoring

- **Sentry**: Error tracking, performance monitoring
- **Prometheus**: CPU, memory, disk, request latency, DB connections
- **UptimeRobot**: External uptime with Telegram alerts
- Alert rules: 5xx > 1%, disk > 85%, memory > 90%

## Additional Resources

### Reference Files

For detailed Docker, Nginx, and script configurations:
- **`references/docker-config.md`** — Dockerfile, docker-compose.prod.yml, .env.example
- **`references/nginx-and-scripts.md`** — Nginx config, security headers, deploy/backup/SSL scripts, CI/CD
