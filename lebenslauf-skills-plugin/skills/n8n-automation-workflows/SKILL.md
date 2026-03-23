---
name: n8n-automation-workflows
description: >
  This skill should be used when the user asks to "set up automation", "create n8n workflows",
  "implement webhooks", "configure Celery tasks", "build email flows",
  "add background processing", "set up cron jobs", "implement Django signals",
  or mentions automation, n8n, webhook, Celery, email flow, background task, cron,
  notification, workflow, signal, async processing, task queue, scheduled jobs,
  email automation, or any automation/workflow feature for the platform.
---

# Automation & Workflow Engine

Automation workflows using n8n (self-hosted) and Django Celery for email automation, webhook processing, DSGVO compliance automation, job scraping callbacks, AI processing, and background tasks.

## Architecture

- n8n (self-hosted on same Hetzner server) for visual workflow orchestration
- Django Celery + Redis for background task queue
- Django signals for event-driven triggers
- Webhook endpoints (DRF API views) for n8n ↔ Django communication

## Webhook Endpoints (Django DRF → n8n)

| Endpoint | Trigger | n8n Action |
|----------|---------|------------|
| `POST /api/v1/webhooks/stripe/` | Stripe events | Route by event type |
| `POST /api/v1/webhooks/apify/` | Scraping results | Ingest + deduplicate jobs |
| `POST /api/v1/webhooks/n8n/` | n8n callbacks | Process workflow results |
| Django signal: user registered | New account | Welcome email flow |
| Django signal: document created | Doc finished | Analytics |
| Celery beat: subscription check | Daily 09:00 | Reminder email |
| Django signal: GDPR request | User request | Process + confirm |

## Celery Tasks

| Task | Purpose | Schedule |
|------|---------|----------|
| `generate_pdf` | Async PDF rendering (WeasyPrint) | On demand |
| `send_transactional_email` | Email via AWS SES | On demand |
| `generate_invoice_pdf` | GoBD invoice generation | On payment |
| `generate_cover_letter` | AI cover letter via Claude API | On demand |
| `check_email_responses` | IMAP polling for reply classification | Every 15 min |
| `process_gdpr_deletion` | Cascade delete + audit log | On request |
| `process_gdpr_export` | Compile user data → ZIP | On request |
| `process_scraping_results` | Ingest Apify webhook data | On webhook |
| `regenerate_sitemap` | Rebuild XML sitemap | On publish |
| `cleanup_expired_data` | Remove data past retention | Daily 03:00 |
| `check_expiring_subscriptions` | Send renewal reminders | Daily 09:00 |

## Django Signals

| Signal | Trigger | Action |
|--------|---------|--------|
| `post_save` on User | New registration | Welcome email task |
| `post_save` on Document | Document completed | Update stats |
| `post_save` on GDPRRequest | New GDPR request | Start async processing |
| `post_save` on JobApplication | Status change | Notification email |
| `post_save` on Payment | Successful payment | Invoice generation task |

## Security

- All webhook endpoints require HMAC signature verification
- Stripe webhooks verified with `stripe.Webhook.construct_event()`
- Apify webhooks verified with shared secret header
- n8n webhooks use shared secret in Authorization header
- Rate limiting on all webhook endpoints (django-ratelimit)

## Email Flows

| Flow | Trigger | Content |
|------|---------|---------|
| Welcome | Registration | Willkommen + getting started |
| Payment confirmation | Successful payment | Bestätigung + invoice PDF |
| Subscription expiring | 7 days before end | Renewal reminder |
| GDPR deletion confirm | Deletion completed | Bestätigung der Löschung |
| GDPR export ready | Export ZIP generated | Download link (24h valid) |
| Application sent | Email sent to company | Confirmation + pipeline link |
| Interview detected | AI classified response | Alert + calendar link |

## Additional Resources

### Reference Files

For detailed Celery task implementations and webhook endpoints:
- **`references/celery-tasks.md`** — Celery config, all tasks, beat schedule, Django signals
- **`references/webhook-endpoints.md`** — DRF webhook views, HMAC verification, n8n workflows
