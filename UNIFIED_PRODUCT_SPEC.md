# GetResume — Unified Product Specification
## Lebenslauf-Builder + Job Automation SaaS for the German Market

> **Version:** 1.0 — 2026-03-04
> **Status:** Architecture Blueprint
> **Stack:** Vue.js 3 SPA + Django 5 REST API + PostgreSQL

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Tech Stack](#2-tech-stack)
3. [Architecture Overview](#3-architecture-overview)
4. [Module Breakdown](#4-module-breakdown)
5. [Database Schema](#5-database-schema)
6. [API Structure](#6-api-structure)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Skills Architecture (Updated)](#8-skills-architecture)
9. [MCP Server Integration](#9-mcp-server-integration)
10. [Subscription Tiers](#10-subscription-tiers)
11. [Legal & Compliance](#11-legal--compliance)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Development Phases](#13-development-phases)

---

## 1. Product Vision

**GetResume** is an end-to-end job-hunting SaaS platform for the German market (Arbeitsmarkt) that combines:

1. **CV Builder** — Build, edit, and optimize German-format Lebenslauf, Bewerbungsschreiben, and Deckblatt with live preview and PDF export
2. **ATS Optimizer** — AI-powered resume optimization to pass Applicant Tracking Systems while avoiding AI-detection flags
3. **Job Scraper** — Automated job collection from LinkedIn, Indeed, StepStone DE via Apify
4. **AI Cover Letter Engine** — Per-job tailored Bewerbungsschreiben generation using Claude API
5. **Email Automation** — Professional application emails sent automatically with cover letter + CV attached
6. **Application Pipeline** — Track every application's status: Applied → Waiting → Rejected / Interview / Follow-up

### User Groups
- **B2C (Primary):** Individual job seekers in Germany
- **B2B Light:** Team accounts for small HR teams / agencies (shared templates, basic role-based access)

### Competitive Landscape
| Competitor | What we add |
|-----------|------------|
| NovoResume | German market focus, legal compliance, job automation |
| Lebenslauf.de | Modern Vue.js editor, AI features, email automation |
| Indeed Apply | Full pipeline tracking, CV builder, cover letter gen |

---

## 2. Tech Stack

### Frontend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Vue.js 3 + TypeScript | SPA with Composition API |
| **State** | Pinia | Centralized store (auth, documents, jobs, pipeline) |
| **Router** | Vue Router 4 | Client-side routing with guards |
| **UI** | Tailwind CSS 3 + Headless UI | Utility-first styling + accessible components |
| **CV Editor** | Custom Vue component | Drag-and-drop (vue-draggable-plus), live preview |
| **Forms** | VeeValidate + Zod | Schema-based validation |
| **HTTP** | Axios | API client with interceptors (auth, refresh, CSRF) |
| **Charts** | Chart.js + vue-chartjs | Dashboard analytics |
| **i18n** | vue-i18n | DE (primary) + EN |
| **Build** | Vite 6 | Fast HMR, tree-shaking, code splitting |

### Backend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Django 5.1 | Core application |
| **API** | Django REST Framework 3.15 | RESTful API with serializers, viewsets |
| **Auth** | dj-rest-auth + SimpleJWT | JWT tokens (access + refresh) |
| **Social Auth** | django-allauth | Google, LinkedIn OAuth |
| **Database** | PostgreSQL 16 | Primary data store |
| **Cache/Queue** | Redis 7 | Caching + Celery broker |
| **Task Queue** | Celery 5 | Async PDF gen, email, scraping callbacks |
| **PDF** | WeasyPrint | HTML → PDF conversion (A4, print CSS) |
| **AI** | Claude API (Anthropic) | Cover letter gen, ATS optimization |
| **Email** | Django Anymail (AWS SES) | Transactional email sending |
| **Storage** | Django Storages + S3 (Hetzner Object Storage) | Media files, PDFs, uploads |
| **Search** | django-filter + PostgreSQL FTS | Job listing search + filtering |

### Scraping & Automation
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Job Scraping** | Apify | LinkedIn, Indeed, StepStone scrapers |
| **Workflow** | n8n (self-hosted) | Visual workflow orchestration |
| **Email Sending** | User's SMTP / Gmail API via OAuth | Application emails (user's own account) |
| **Email Tracking** | IMAP polling + webhook classification | Response monitoring |

### Infrastructure
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Server** | Hetzner Cloud (CX31+) | EU data residency (Falkenstein/Nuremberg) |
| **Container** | Docker + Docker Compose | All services containerized |
| **Reverse Proxy** | Nginx | SSL termination, static files, rate limiting |
| **SSL** | Let's Encrypt (Certbot) | Auto-renewed HTTPS |
| **CI/CD** | GitHub Actions | Test → Build → Deploy pipeline |
| **Monitoring** | Sentry + Prometheus + Grafana | Error tracking + metrics |
| **CDN** | Cloudflare | Static assets, DDoS protection |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE CDN                            │
│                   (DNS + DDoS + Cache)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    NGINX REVERSE PROXY                       │
│              (SSL, rate limit, security headers)             │
├────────────┬─────────────────┬──────────────────────────────┤
│            │                 │                              │
│   /api/*   │    /admin/*     │    /*  (static SPA)          │
│            │                 │                              │
▼            ▼                 ▼                              │
┌────────────────────┐  ┌──────────────────┐                  │
│   DJANGO API       │  │   VUE.JS SPA     │ ◄── Vite build  │
│   (Gunicorn)       │  │   (static files) │    served by     │
│                    │  └──────────────────┘    Nginx          │
│  ┌──────────────┐  │                                        │
│  │ DRF ViewSets │  │                                        │
│  │ JWT Auth     │  │                                        │
│  │ Serializers  │  │                                        │
│  └──────┬───────┘  │                                        │
│         │          │                                        │
│  ┌──────▼───────┐  │  ┌─────────────┐  ┌─────────────────┐ │
│  │ PostgreSQL   │  │  │ Redis       │  │ Celery Workers  │ │
│  │ (primary DB) │  │  │ (cache +    │  │ (PDF, email,    │ │
│  │              │  │  │  broker)    │  │  AI, scraping)  │ │
│  └──────────────┘  │  └─────────────┘  └────────┬────────┘ │
└────────────────────┘                            │          │
                                                  │          │
┌─────────────────────────────────────────────────┘          │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Apify       │  │ Claude API   │  │ n8n               │  │
│  │ (scraping)  │  │ (AI gen)     │  │ (workflow engine)  │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Stripe      │  │ AWS SES      │  │ Hetzner Object    │  │
│  │ (payments)  │  │ (trans.email)│  │ Storage (S3)      │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Monolith vs Micro | **Django monolith** | Single team, faster iteration, shared DB models |
| Frontend | **Vue.js SPA** | Rich editor UX, real-time preview, complex state |
| API | **REST (DRF)** | Simpler than GraphQL, sufficient for CRUD + some custom endpoints |
| Auth | **JWT (access + refresh)** | Stateless API, works with SPA, mobile-ready |
| PDF | **WeasyPrint (server-side)** | HTML/CSS → PDF, German A4 format, print styles |
| AI | **Claude API** | Best at nuanced German writing, anti-AI-detection |
| Scraping | **Apify (external)** | Managed infrastructure, handles anti-bot, pre-built actors |
| Email sending | **User's own Gmail/SMTP** | Avoids deliverability issues, emails come from user |
| Queue | **Celery + Redis** | Battle-tested, Django-native, handles PDF + email async |

---

## 4. Module Breakdown

### Module 1: Authentication & User Management (`accounts/`)
- Registration (email + password, Google OAuth, LinkedIn OAuth)
- JWT login/logout with refresh token rotation
- Email verification + password reset
- User profile with German-specific fields
- Team accounts (B2B light): invite members, roles (Admin/Member)
- DSGVO user rights: data export, account deletion

### Module 2: CV Builder & Editor (`documents/`)
**The core product — Vue.js drag-and-drop editor with live preview**

- Document types: Lebenslauf, Bewerbungsschreiben, Deckblatt
- Template catalog with categories (Klassisch, Modern, Kreativ, IT, Akademisch, etc.)
- German CV sections:
  - Persönliche Daten (photo, Geburtsdatum, Familienstand, Staatsangehörigkeit)
  - Berufserfahrung (sortable, repeatable, anti-chronologisch)
  - Ausbildung (sortable, repeatable)
  - Kenntnisse (skill bars: Grundkenntnisse → Experte)
  - Sprachen (CEFR A1–C2 + Muttersprache)
  - Weiterbildungen, Zertifikate
  - Ehrenamt, Interessen
  - Unterschrift (Ort + Datum)
- Live HTML preview in split-pane (editor left, preview right)
- PDF export via WeasyPrint (A4 format)
- Photo upload with client-side crop (Cropper.js)
- Autosave (debounced 2s → API PATCH)
- 74 color themes + font selection (Free: 3 fonts/30 themes, Premium: all)
- Bewerbungsmappe: combine Deckblatt + Lebenslauf + Anschreiben → single PDF

### Module 3: ATS Optimization (`ats/`)
**AI-powered resume analysis to beat Applicant Tracking Systems**

- ATS score calculation (keyword match, formatting, section completeness)
- Keyword extraction from job descriptions
- Resume-to-job matching score
- Suggestions: missing keywords, section improvements, formatting fixes
- Anti-AI-detection: humanization pass that varies sentence structure, adds natural imperfections
- Claude API integration for rewriting sections

### Module 4: Job Scraping (`jobs/`)
**Automated job collection from German platforms**

- Apify integration with pre-built actors:
  - LinkedIn Jobs Scraper
  - Indeed Scraper
  - StepStone DE Scraper
- User configures: keywords, location (Stadt/PLZ), radius, job type (Vollzeit/Teilzeit/Mini-Job)
- Webhook-based results ingestion (Apify → Django webhook → PostgreSQL)
- Structured data stored: title, company, location, description, requirements, salary range, contact person, posting URL, application deadline
- Job listing table with filters and search (Vue.js DataTable)
- Deduplication by URL + company + title hash
- Scraping runs: on-demand (user clicks) or scheduled (daily/weekly)
- Export to Excel (xlsx) via DRF + openpyxl

### Module 5: AI Cover Letter Engine (`coverletters/`)
**Per-job tailored Bewerbungsschreiben generation**

- Claude API prompt engineering for German business letters
- Input: user's CV data (JSON) + job description + company info
- Output: professional Bewerbungsschreiben in DIN 5008 format
- Tone control: formal/semi-formal/creative
- Anti-AI-detection: natural language variations, personal anecdotes injection
- User can edit generated letter before sending
- Saves to documents as Bewerbungsschreiben type
- Regeneration with different angle/emphasis

### Module 6: Email Automation (`emails/`)
**Automated professional application emails**

- Email composition: subject line + body + attachments (CV PDF + cover letter PDF)
- Contact person addressing from scraped data
- User authenticates their Gmail via OAuth2 / provides SMTP credentials
- Emails sent from user's own account (not platform's domain)
- Scheduling: immediate, delayed, batch send with intervals
- Template: professional German email with greeting + reference + attachments note
- Anti-spam: random delays between sends, human-like send patterns

### Module 7: Application Pipeline (`pipeline/`)
**Track every job application through its lifecycle**

- States: `discovered` → `applied` → `waiting` → `rejected` | `interview` | `follow_up` | `offer`
- Kanban board view (Vue.js draggable columns)
- Table view with sorting/filtering
- Email response monitoring:
  - User connects Gmail via OAuth2 (read-only)
  - Celery task polls IMAP inbox for replies from applied companies
  - Claude API classifies response: rejection, interview invite, follow-up request, offer
  - Auto-updates pipeline state
- Analytics: response rate, average response time, success rate by platform
- Notes and reminders per application
- Calendar integration for interview scheduling

### Module 8: Payments & Billing (`payments/`)
**Stripe integration optimized for German market**

- Payment methods (priority for DE):
  1. Kreditkarte (Visa/Mastercard) via Stripe Elements
  2. PayPal via Stripe
  3. SEPA-Lastschrift
  4. Sofortüberweisung/Klarna
  5. Giropay
  6. Apple Pay / Google Pay
- PAngV compliance: all prices "inkl. MwSt" (19%)
- Checkout flow with legal checkboxes (AGB + Widerrufsbelehrung)
- Stripe Checkout Sessions for PCI compliance
- Webhook handler: payment_intent.succeeded → activate subscription
- GoBD-compliant invoice generation (sequential Rechnungsnummer)
- 14-day Widerrufsrecht with automated refund
- Subscription management in user dashboard

### Module 9: Legal & Compliance (`legal/`)
**German law compliance — DSGVO, TMG, TTDSG, BGB, GoBD**

- Impressum (TMG §5 / DDG Art. 5) — 2-click accessible
- Datenschutzerklärung (Art. 13/14 DSGVO) — comprehensive privacy policy
- Cookie Consent Banner (TTDSG §25):
  - Layer 1: "Alle akzeptieren" | "Einstellungen" | "Nur notwendige"
  - Layer 2: Granular toggles (Notwendig, Statistik, Marketing, Externe Medien)
  - Layer 3: Full cookie table
  - Server-side blocking of tracking before consent
- AGB (Terms of Service) with ODR link
- Widerrufsbelehrung + model withdrawal form
- DSGVO user rights: Art. 15 (access), Art. 17 (erasure), Art. 20 (portability)
- Consent logging with UUID, timestamp, hashed IP, choices
- Google Fonts self-hosted (LG München ruling)
- Audit log for all data processing activities

### Module 10: Dashboard (`dashboard/`)
**User and admin interfaces**

#### User Dashboard (Mein Bereich)
- Sidebar: Meine Dokumente, Jobs, Bewerbungen, Konto, Abo & Zahlung, Datenschutz
- Document grid/list with actions (edit, duplicate, download, delete)
- Job scraping controls and results
- Application pipeline (Kanban + table)
- Subscription status + payment history
- DSGVO controls (export data, delete account)

#### Admin Dashboard
- Revenue: MRR, ARR, conversion rate, churn
- Users: total, active, premium, new this month
- Documents: created today/week/month, popular templates
- DSGVO panel: pending requests, audit log
- Content management: templates, blog posts

#### B2B Light Dashboard
- Team member management (invite, remove, role change)
- Shared template library
- Usage analytics per team member

### Module 11: Blog & SEO (`blog/`)
**Karriere-Blog for organic growth**

- Blog with categories and tags (DE-optimized URLs)
- URL structure: /karriere-blog/{slug}/
- django-meta for per-page meta tags
- JSON-LD structured data (BlogPosting, Organization, Product, FAQPage, HowTo)
- XML sitemap with auto-regeneration
- Breadcrumb navigation
- Internal linking: blog ↔ templates ↔ editor CTAs
- Target keywords: Lebenslauf Vorlage, Lebenslauf erstellen, Bewerbungsschreiben Muster

### Module 12: Automation (`automation/`)
**Background processing and workflow orchestration**

- Celery tasks: PDF gen, email dispatch, AI generation, GDPR processing, sitemap regen
- n8n workflows: welcome email, payment confirmation, subscription reminders, GDPR flows
- Django signals: trigger workflows on user actions
- Webhook endpoints with HMAC verification
- Scheduled jobs: scraping runs, email checking, data cleanup

---

## 5. Database Schema

### Core Models

```
┌─────────────────────┐     ┌─────────────────────┐
│ User                │     │ UserProfile          │
├─────────────────────┤     ├─────────────────────┤
│ id (UUID)           │◄───►│ user_id (FK)         │
│ email               │     │ first_name           │
│ password (hashed)   │     │ last_name            │
│ is_active           │     │ geburtsdatum         │
│ is_staff            │     │ geburtsort           │
│ date_joined         │     │ staatsangehoerigkeit │
│ last_login          │     │ familienstand        │
│ deleted_at (soft)   │     │ photo                │
│ team_id (FK, null)  │     │ phone                │
│ team_role           │     │ address_json         │
└─────────────────────┘     │ linkedin_url         │
                            │ website_url          │
                            └─────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│ Team                │     │ TeamInvite           │
├─────────────────────┤     ├─────────────────────┤
│ id (UUID)           │     │ id (UUID)            │
│ name                │     │ team_id (FK)         │
│ owner_id (FK User)  │     │ email                │
│ max_members         │     │ role                 │
│ created_at          │     │ token                │
└─────────────────────┘     │ expires_at           │
                            └─────────────────────┘

┌──────────────────────────┐     ┌─────────────────────┐
│ Document                 │     │ Template             │
├──────────────────────────┤     ├─────────────────────┤
│ id (UUID)                │     │ id (UUID)            │
│ user_id (FK)             │     │ name                 │
│ template_id (FK)         │     │ category             │
│ doc_type (enum)          │     │ html_template        │
│   lebenslauf             │     │ css_template         │
│   bewerbungsschreiben    │     │ thumbnail_url        │
│   deckblatt              │     │ is_premium           │
│ title                    │     │ is_active            │
│ content (JSONField)      │     │ sort_order           │
│ theme_id (FK)            │     └─────────────────────┘
│ custom_styles (JSON)     │
│ pdf_file (FileField)     │     ┌─────────────────────┐
│ pdf_generated_at         │     │ Theme                │
│ ats_score (int, null)    │     ├─────────────────────┤
│ is_optimized (bool)      │     │ id (UUID)            │
│ created_at               │     │ name                 │
│ updated_at               │     │ primary_color        │
│ deleted_at (soft)        │     │ secondary_color      │
└──────────────────────────┘     │ accent_color         │
                                 │ font_heading         │
                                 │ font_body            │
                                 │ is_premium           │
                                 └─────────────────────┘

┌──────────────────────────┐     ┌─────────────────────────┐
│ ScrapedJob               │     │ ScrapingRun             │
├──────────────────────────┤     ├─────────────────────────┤
│ id (UUID)                │     │ id (UUID)               │
│ user_id (FK)             │     │ user_id (FK)            │
│ scraping_run_id (FK)     │     │ platform (enum)         │
│ platform (enum)          │     │   linkedin/indeed/      │
│ external_id (hash)       │     │   stepstone             │
│ title                    │     │ keywords                │
│ company_name             │     │ location                │
│ company_url              │     │ radius_km               │
│ location                 │     │ job_type                │
│ description (text)       │     │ status (enum)           │
│ requirements (text)      │     │   pending/running/      │
│ salary_range (JSON)      │     │   completed/failed      │
│ job_type (enum)          │     │ jobs_found (int)        │
│ contact_person           │     │ apify_run_id            │
│ contact_email            │     │ started_at              │
│ posting_url              │     │ completed_at            │
│ application_deadline     │     │ schedule (cron, null)   │
│ is_remote                │     └─────────────────────────┘
│ scraped_at               │
│ dedup_hash (unique)      │
│ raw_data (JSON)          │
└──────────────────────────┘

┌──────────────────────────┐     ┌─────────────────────────┐
│ JobApplication           │     │ ApplicationEmail        │
├──────────────────────────┤     ├─────────────────────────┤
│ id (UUID)                │     │ id (UUID)               │
│ user_id (FK)             │     │ application_id (FK)     │
│ job_id (FK ScrapedJob)   │     │ direction (enum)        │
│ document_id (FK, CV)     │     │   sent/received         │
│ cover_letter_id (FK)     │     │ subject                 │
│ status (enum)            │     │ body (text)             │
│   discovered             │     │ from_email              │
│   applied                │     │ to_email                │
│   waiting                │     │ attachments (JSON)      │
│   rejected               │     │ message_id              │
│   interview              │     │ sent_at / received_at   │
│   follow_up              │     │ classification (enum)   │
│   offer                  │     │   rejection/interview/  │
│ applied_at               │     │   follow_up/offer/other │
│ response_at              │     │ classified_by (ai/manual│
│ interview_date           │     └─────────────────────────┘
│ notes (text)             │
│ reminder_at              │
│ updated_at               │
└──────────────────────────┘

┌──────────────────────────┐     ┌─────────────────────────┐
│ Subscription             │     │ Payment                 │
├──────────────────────────┤     ├─────────────────────────┤
│ id (UUID)                │     │ id (UUID)               │
│ user_id (FK)             │     │ user_id (FK)            │
│ plan (enum)              │     │ subscription_id (FK)    │
│   free/premium/business  │     │ stripe_payment_id       │
│ stripe_customer_id       │     │ amount_net              │
│ stripe_subscription_id   │     │ mwst_rate (19%)         │
│ status (enum)            │     │ mwst_amount             │
│   active/cancelled/      │     │ amount_gross            │
│   past_due/trialing      │     │ currency (EUR)          │
│ current_period_start     │     │ status                  │
│ current_period_end       │     │ payment_method          │
│ cancel_at_period_end     │     │ paid_at                 │
│ widerruf_deadline        │     └─────────────────────────┘
│ created_at               │
└──────────────────────────┘     ┌─────────────────────────┐
                                 │ Invoice                 │
┌──────────────────────────┐     ├─────────────────────────┤
│ CookieConsent            │     │ id (UUID)               │
├──────────────────────────┤     │ payment_id (FK)         │
│ id (UUID)                │     │ user_id (FK)            │
│ user_id (FK, null)       │     │ rechnungsnummer         │
│ session_key              │     │   (RE-2026-00001)       │
│ consent_version          │     │ rechnungsdatum          │
│ necessary (always true)  │     │ leistungszeitraum       │
│ statistics (bool)        │     │ nettobetrag             │
│ marketing (bool)         │     │ mwst_satz               │
│ external_media (bool)    │     │ mwst_betrag             │
│ ip_hash                  │     │ bruttobetrag            │
│ user_agent               │     │ pdf_file                │
│ granted_at               │     │ company_details (JSON)  │
│ revoked_at (null)        │     │ created_at              │
└──────────────────────────┘     └─────────────────────────┘

┌──────────────────────────┐     ┌─────────────────────────┐
│ GDPRRequest              │     │ AuditLog                │
├──────────────────────────┤     ├─────────────────────────┤
│ id (UUID)                │     │ id (UUID)               │
│ user_id (FK)             │     │ user_id (FK)            │
│ request_type (enum)      │     │ action                  │
│   access/deletion/       │     │ model_name              │
│   export/rectification   │     │ object_id               │
│ status (enum)            │     │ changes (JSON)          │
│   pending/processing/    │     │ ip_address (hashed)     │
│   completed/rejected     │     │ timestamp               │
│ requested_at             │     └─────────────────────────┘
│ completed_at             │
│ export_file (null)       │     ┌─────────────────────────┐
│ notes                    │     │ EmailCredential         │
└──────────────────────────┘     ├─────────────────────────┤
                                 │ id (UUID)               │
┌──────────────────────────┐     │ user_id (FK)            │
│ BlogPost                 │     │ provider (enum)         │
├──────────────────────────┤     │   gmail/smtp/outlook    │
│ id (UUID)                │     │ email_address           │
│ title                    │     │ oauth_token (encrypted) │
│ slug                     │     │ smtp_host (encrypted)   │
│ content (text)           │     │ smtp_port               │
│ excerpt                  │     │ smtp_username (encrypted│
│ category_id (FK)         │     │ smtp_password (encrypted│
│ author_id (FK User)      │     │ is_verified             │
│ meta_title               │     │ last_used_at            │
│ meta_description         │     └─────────────────────────┘
│ og_image                 │
│ structured_data (JSON)   │
│ is_published             │
│ published_at             │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

---

## 6. API Structure

### URL Namespace

```
/api/v1/
├── auth/
│   ├── register/              POST    Create account
│   ├── login/                 POST    Get JWT tokens
│   ├── token/refresh/         POST    Refresh access token
│   ├── password/reset/        POST    Request password reset
│   ├── password/reset/confirm/ POST   Confirm reset
│   ├── google/                POST    Google OAuth callback
│   └── linkedin/              POST    LinkedIn OAuth callback
│
├── users/
│   ├── me/                    GET     Current user profile
│   ├── me/                    PATCH   Update profile
│   ├── me/photo/              POST    Upload profile photo
│   ├── me/gdpr/export/        POST    Request data export
│   ├── me/gdpr/delete/        POST    Request account deletion
│   └── me/email-credentials/  CRUD    Email sending credentials
│
├── teams/                     (B2B Light)
│   ├──                        POST    Create team
│   ├── {id}/                  GET     Team details
│   ├── {id}/members/          GET     List members
│   ├── {id}/invite/           POST    Invite member
│   └── {id}/members/{uid}/    DELETE  Remove member
│
├── documents/
│   ├──                        GET     List user's documents
│   ├──                        POST    Create new document
│   ├── {id}/                  GET     Document detail
│   ├── {id}/                  PATCH   Update content (autosave)
│   ├── {id}/                  DELETE  Soft delete
│   ├── {id}/duplicate/        POST    Clone document
│   ├── {id}/pdf/              GET     Download PDF (generate if stale)
│   ├── {id}/preview/          GET     HTML preview
│   ├── {id}/ats-score/        GET     Calculate ATS score
│   └── {id}/optimize/         POST    AI optimization suggestions
│
├── templates/
│   ├──                        GET     List templates (with category filter)
│   ├── {id}/                  GET     Template detail
│   └── {id}/preview/          GET     Template preview with sample data
│
├── themes/
│   └──                        GET     List available themes
│
├── jobs/
│   ├──                        GET     List scraped jobs (filtered)
│   ├── {id}/                  GET     Job detail
│   ├── {id}/                  DELETE  Remove from list
│   ├── scraping-runs/         GET     List user's scraping runs
│   ├── scraping-runs/         POST    Start new scraping run
│   ├── scraping-runs/{id}/    GET     Scraping run status
│   └── export/                GET     Export jobs to XLSX
│
├── coverletters/
│   ├── generate/              POST    Generate cover letter for job
│   ├── {id}/regenerate/       POST    Regenerate with different angle
│   └── {id}/                  PATCH   Edit generated letter
│
├── applications/
│   ├──                        GET     List all applications (pipeline)
│   ├──                        POST    Create application (apply to job)
│   ├── {id}/                  GET     Application detail
│   ├── {id}/                  PATCH   Update status, notes
│   ├── {id}/send-email/       POST    Send application email
│   ├── stats/                 GET     Pipeline analytics
│   └── check-responses/       POST    Trigger email response check
│
├── payments/
│   ├── plans/                 GET     List subscription plans
│   ├── checkout/              POST    Create Stripe Checkout Session
│   ├── subscription/          GET     Current subscription
│   ├── subscription/cancel/   POST    Cancel subscription
│   ├── subscription/widerruf/ POST    Exercise Widerrufsrecht
│   ├── invoices/              GET     List invoices
│   ├── invoices/{id}/pdf/     GET     Download invoice PDF
│   └── webhooks/stripe/       POST    Stripe webhook handler
│
├── blog/
│   ├──                        GET     List published posts
│   ├── {slug}/                GET     Post detail
│   ├── categories/            GET     List categories
│   └── sitemap.xml            GET     XML sitemap
│
├── legal/
│   ├── cookie-consent/        POST    Save cookie preferences
│   ├── cookie-consent/        GET     Get current preferences
│   └── impressum/             GET     Impressum data
│
└── webhooks/
    ├── apify/                 POST    Apify scraping results
    ├── stripe/                POST    Stripe payment events
    └── n8n/                   POST    n8n workflow callbacks
```

---

## 7. Frontend Architecture

### Vue.js SPA Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── main.ts                    # App entry
│   ├── App.vue                    # Root component
│   ├── router/
│   │   └── index.ts               # Vue Router config + guards
│   ├── stores/                    # Pinia stores
│   │   ├── auth.ts                # User auth state
│   │   ├── documents.ts           # CV documents
│   │   ├── editor.ts              # Editor state (active doc, undo/redo)
│   │   ├── jobs.ts                # Scraped jobs
│   │   ├── pipeline.ts            # Application pipeline
│   │   ├── subscription.ts        # Plan + billing
│   │   └── consent.ts             # Cookie consent state
│   ├── api/                       # Axios service layer
│   │   ├── client.ts              # Axios instance + interceptors
│   │   ├── auth.ts                # Auth endpoints
│   │   ├── documents.ts           # Document CRUD
│   │   ├── jobs.ts                # Job scraping
│   │   ├── applications.ts        # Pipeline
│   │   └── payments.ts            # Stripe
│   ├── components/
│   │   ├── common/                # Shared (Button, Modal, DataTable, etc.)
│   │   ├── editor/                # CV Editor components
│   │   │   ├── EditorLayout.vue   # Split pane (editor + preview)
│   │   │   ├── SectionList.vue    # Draggable section list
│   │   │   ├── SectionForm.vue    # Generic section form
│   │   │   ├── PhotoUpload.vue    # Photo upload + crop
│   │   │   ├── SkillRating.vue    # Skill bar component
│   │   │   ├── LanguageLevel.vue  # CEFR level selector
│   │   │   ├── LivePreview.vue    # HTML preview iframe
│   │   │   ├── TemplateSelector.vue
│   │   │   └── ThemePicker.vue
│   │   ├── jobs/                  # Job scraping components
│   │   │   ├── JobTable.vue       # Filterable job list
│   │   │   ├── JobDetail.vue      # Full job view
│   │   │   ├── ScrapingConfig.vue # Platform + keyword config
│   │   │   └── JobActions.vue     # Apply / Generate CL / Dismiss
│   │   ├── pipeline/              # Application tracking
│   │   │   ├── KanbanBoard.vue    # Draggable columns
│   │   │   ├── PipelineTable.vue  # Table view
│   │   │   ├── ApplicationCard.vue
│   │   │   └── PipelineStats.vue  # Analytics charts
│   │   ├── dashboard/             # Dashboard sections
│   │   ├── payment/               # Checkout, plans
│   │   ├── legal/                 # Cookie banner, consent
│   │   └── blog/                  # Blog list, article
│   ├── views/                     # Route-level components
│   │   ├── HomeView.vue           # Landing page
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── DashboardView.vue      # Mein Bereich
│   │   ├── EditorView.vue         # CV Editor
│   │   ├── JobsView.vue           # Job scraping
│   │   ├── PipelineView.vue       # Application pipeline
│   │   ├── PricingView.vue        # Preise
│   │   ├── CheckoutView.vue
│   │   ├── BlogListView.vue
│   │   ├── BlogPostView.vue
│   │   ├── ImpressumView.vue
│   │   ├── DatenschutzView.vue
│   │   └── AGBView.vue
│   ├── composables/               # Vue composables
│   │   ├── useAuth.ts
│   │   ├── useDebounce.ts
│   │   ├── useAutoSave.ts
│   │   └── useCookieConsent.ts
│   ├── utils/
│   │   ├── validators.ts
│   │   └── formatters.ts          # German date/number formatting
│   ├── i18n/
│   │   ├── de.json
│   │   └── en.json
│   └── assets/
│       ├── fonts/                 # Self-hosted (no Google Fonts CDN)
│       └── styles/
│           └── tailwind.css
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Route Map

| Route | View | Auth | Plan |
|-------|------|------|------|
| `/` | Landing page | No | — |
| `/login` | Login | No | — |
| `/registrieren` | Register | No | — |
| `/preise` | Pricing | No | — |
| `/karriere-blog` | Blog list | No | — |
| `/karriere-blog/:slug` | Blog post | No | — |
| `/impressum` | Impressum | No | — |
| `/datenschutz` | Privacy policy | No | — |
| `/agb` | Terms | No | — |
| `/dashboard` | Mein Bereich | Yes | Free+ |
| `/editor/:id` | CV Editor | Yes | Free+ |
| `/jobs` | Job scraping | Yes | Premium+ |
| `/bewerbungen` | Application pipeline | Yes | Premium+ |
| `/konto` | Account settings | Yes | Free+ |
| `/abo` | Subscription management | Yes | Free+ |
| `/checkout` | Stripe checkout | Yes | — |
| `/admin` | Admin dashboard | Staff | — |

---

## 8. Skills Architecture (Updated for Vue.js SPA)

The existing 9 skills need updating, and 4 new skills are added for automation features.

### Updated Skills (HTMX → Vue.js + DRF)

| # | Old Skill | New Skill | Key Changes |
|---|----------|----------|-------------|
| 1 | `django-lebenslauf-core` | `django-api-core` | Add DRF serializers, JWT config, CORS setup |
| 2 | `german-legal-compliance` | `german-legal-compliance` | API endpoints for consent, legal pages as API data |
| 3 | `lebenslauf-templates` | `lebenslauf-templates` | Server-side rendering only for PDF, preview via API |
| 4 | `htmx-editor-components` | `vue-cv-editor` | Complete rewrite as Vue.js components |
| 5 | `stripe-payment-de` | `stripe-payment-de` | API views instead of Django templates |
| 6 | `dashboard-htmx` | `vue-dashboard` | Vue.js dashboard components |
| 7 | `karriere-blog-seo` | `karriere-blog-seo` | DRF API + Vue.js blog views, SSR consideration for SEO |
| 8 | `n8n-automation-workflows` | `n8n-automation-workflows` | Mostly unchanged |
| 9 | `deployment-hetzner` | `deployment-hetzner` | Add Vue.js build step, SPA serving via Nginx |

### New Skills (Automation Layer)

| # | Skill | Purpose |
|---|-------|---------|
| 10 | `apify-job-scraper` | Apify integration, job models, webhook ingestion, deduplication |
| 11 | `ai-cover-letter-engine` | Claude API integration, prompt engineering, DIN 5008 formatting |
| 12 | `email-automation-de` | Gmail OAuth, SMTP, email sending, IMAP response monitoring |
| 13 | `application-pipeline` | Pipeline models, Kanban API, response classification, analytics |

### Install Order (Updated)

```
Phase 1 — Foundation
  1. django-api-core            ← DRF, JWT, models, settings
  2. german-legal-compliance    ← CRITICAL: legal framework
  3. vue-frontend-setup         ← Vue.js project scaffolding

Phase 2 — Core Product
  4. lebenslauf-templates       ← Template system + PDF rendering
  5. vue-cv-editor              ← The editor (core value)
  6. stripe-payment-de          ← Monetization

Phase 3 — Automation
  7. apify-job-scraper          ← Job collection
  8. ai-cover-letter-engine     ← AI cover letter generation
  9. email-automation-de        ← Email sending + tracking
  10. application-pipeline      ← Pipeline tracking

Phase 4 — Growth & Operations
  11. vue-dashboard             ← User + admin dashboards
  12. karriere-blog-seo         ← SEO growth engine
  13. n8n-automation-workflows  ← Operational automation

Phase 5 — Launch
  14. deployment-hetzner        ← Production deployment
```

---

## 9. MCP Server Integration

### Active MCP Servers (from prompt_mcp.md)

| Server | Phase | Purpose in GetResume |
|--------|-------|---------------------|
| **Stripe** | Phase 1 | Payment testing from day one |
| **PostgreSQL** | Phase 1 | Direct DB access for debugging |
| **GitHub** | Phase 1 | Repo management, CI/CD |
| **n8n** (connected) | Phase 3 | Workflow orchestration |
| **Cloudflare** (connected) | Phase 5 | CDN, DNS |
| **Indeed** (connected) | Phase 3 | Job listing integration |
| **Gmail** (connected) | Phase 3 | Email automation testing |
| **Sentry** | Phase 4 | Error tracking |
| **Puppeteer** | Phase 4 | E2E testing, template screenshots |

### Custom MCP via n8n
1. **PDF Generator** — Trigger CV PDF generation
2. **DSGVO Checker** — Audit compliance on any page
3. **Invoice Generator** — GoBD invoice creation
4. **Template Preview** — Screenshot generation for catalog

---

## 10. Subscription Tiers

| Feature | Kostenlos | Premium (9,99€/mo) | Business (24,99€/mo) |
|---------|-----------|--------------------|--------------------|
| Lebenslauf erstellen | 1 document | Unlimited | Unlimited |
| Templates | 3 basic | All (25+) | All + custom |
| Farbthemen | 30 | 74 | 74 + custom |
| Schriftarten | 3 | 12 | 12 + upload |
| PDF Download | Watermark | Clean PDF | Clean PDF |
| Bewerbungsschreiben | — | Unlimited | Unlimited |
| Deckblatt | — | Unlimited | Unlimited |
| Bewerbungsmappe | — | Yes | Yes |
| ATS Score | Basic | Advanced + suggestions | Advanced |
| **Job Scraping** | — | 50 jobs/month | 500 jobs/month |
| **AI Cover Letter** | — | 10/month | 100/month |
| **Email Automation** | — | 20 emails/month | 200 emails/month |
| **Pipeline Tracking** | — | Yes | Yes |
| **Response Monitoring** | — | Yes | Yes |
| Team Members | — | — | Up to 5 |
| Shared Templates | — | — | Yes |
| Priority Support | — | Email | Email + Chat |
| Prices shown | inkl. MwSt | inkl. MwSt | inkl. MwSt |

**Annual discount:** 2 months free (yearly billing)

---

## 11. Legal & Compliance

### Risk Matrix

| Risk | Severity | Mitigation |
|------|----------|-----------|
| DSGVO violation | **CRITICAL** (up to €20M / 4% revenue) | Full compliance framework, DPO, audit log |
| Job scraping ToS violation | **HIGH** | User-initiated scraping, no bulk automation, respect robots.txt |
| UWG §7 unsolicited emails | **HIGH** | Emails from user's own account, user takes responsibility, disclaimer |
| Missing Impressum | **HIGH** (€50K fine) | Auto-generated, 2-click accessible |
| Cookie consent violation | **MEDIUM** | TTDSG §25 compliant banner, server-side blocking |
| Invoice non-compliance | **MEDIUM** | GoBD sequential numbering, 10-year retention |

### Legal Disclaimers Required
- Terms of Service: user is responsible for email content and scraping usage
- Privacy Policy: covers AI processing, third-party data handling
- Cookie Banner: blocks all tracking pre-consent
- Job scraping: "This tool collects publicly available job listings. Use responsibly."
- Email automation: "Emails are sent from your personal account. You are responsible for compliance with applicable laws."

---

## 12. Deployment Architecture

### Hetzner Cloud Setup

```
Hetzner CX31 (4 vCPU, 8GB RAM, 80GB SSD)
├── Docker Compose Stack:
│   ├── nginx (reverse proxy + SSL + SPA serving)
│   ├── django-api (Gunicorn, 4 workers)
│   ├── celery-worker (2 workers)
│   ├── celery-beat (scheduler)
│   ├── postgresql-16
│   ├── redis-7
│   └── n8n (self-hosted)
├── Volumes:
│   ├── /data/postgres/ (DB persistent)
│   ├── /data/redis/ (cache persistent)
│   ├── /data/media/ (uploads, PDFs)
│   └── /data/n8n/ (workflow data)
└── Cron:
    ├── certbot-renew (daily)
    ├── db-backup (daily → S3)
    └── log-rotate (weekly)
```

### CI/CD Pipeline (GitHub Actions)

```
Push to main →
  1. Run Django tests (pytest)
  2. Run Vue.js tests (Vitest)
  3. Lint (ruff + eslint)
  4. Build Vue.js SPA (vite build)
  5. Build Docker image
  6. Push to GitHub Container Registry
  7. SSH deploy to Hetzner (docker compose pull + up)
  8. Health check
  9. Notify Sentry of release
```

---

## 13. Development Phases

### Phase 1: Foundation (Weeks 1–3)
- [ ] Django project setup with DRF, JWT auth, PostgreSQL
- [ ] Vue.js project scaffolding (Vite, Pinia, Vue Router, Tailwind)
- [ ] User registration/login (email + Google OAuth)
- [ ] User profile CRUD
- [ ] Basic API structure and Swagger docs
- [ ] Cookie consent banner (TTDSG compliant)
- [ ] Impressum + Datenschutzerklärung pages
- [ ] Docker Compose local dev environment

### Phase 2: Core Product (Weeks 4–8)
- [ ] Template system (5 initial templates)
- [ ] Vue.js CV editor with drag-and-drop sections
- [ ] Live HTML preview
- [ ] PDF generation (WeasyPrint)
- [ ] Photo upload + crop
- [ ] German CV sections (all types)
- [ ] Theme and font selection
- [ ] Autosave
- [ ] ATS score calculation (basic)
- [ ] Stripe integration + checkout flow
- [ ] Subscription management
- [ ] GoBD invoice generation

### Phase 3: Automation (Weeks 9–13)
- [ ] Apify integration + webhook handler
- [ ] Job scraping UI (config + results table)
- [ ] Job deduplication and storage
- [ ] AI cover letter generation (Claude API)
- [ ] Email credential management (Gmail OAuth / SMTP)
- [ ] Email sending with CV + cover letter attachments
- [ ] Application pipeline (Kanban board)
- [ ] Email response monitoring (IMAP polling)
- [ ] Response classification (Claude API)
- [ ] Pipeline analytics

### Phase 4: Growth & Polish (Weeks 14–17)
- [ ] Full user dashboard (Mein Bereich)
- [ ] Admin dashboard with analytics
- [ ] Karriere-Blog with SEO
- [ ] B2B light: team accounts
- [ ] n8n workflows (welcome, payment, reminders)
- [ ] ATS optimization (advanced, with Claude)
- [ ] Bewerbungsmappe builder
- [ ] Excel export for jobs
- [ ] Widerrufsrecht flow

### Phase 5: Launch (Weeks 18–19)
- [ ] Hetzner deployment + Docker
- [ ] Nginx + SSL + security headers
- [ ] Sentry error tracking
- [ ] Performance optimization
- [ ] Legal review final pass
- [ ] Monitoring + alerting
- [ ] Beta launch with 50 users
- [ ] Iterate on feedback

---

## Appendix: Django App Structure

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
│   ├── accounts/         # User, Profile, Team, Auth
│   ├── documents/        # Document, Template, Theme
│   ├── ats/              # ATS scoring + optimization
│   ├── jobs/             # ScrapedJob, ScrapingRun
│   ├── coverletters/     # AI cover letter generation
│   ├── emails/           # EmailCredential, sending, tracking
│   ├── pipeline/         # JobApplication, ApplicationEmail
│   ├── payments/         # Subscription, Payment, Invoice
│   ├── legal/            # CookieConsent, GDPRRequest, AuditLog
│   ├── blog/             # BlogPost, Category, Tag
│   └── automation/       # Celery tasks, signals, webhook handlers
├── templates/            # PDF templates only (WeasyPrint)
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
