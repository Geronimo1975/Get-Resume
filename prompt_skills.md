# Prompt Skills - Lebenslauf-Builder SaaS Platform (Piața Germană)

## Cuprins

1. [Skills Existente de Folosit](#1-skills-existente-deja-disponibile-in-claude)
2. [Skills Custom de Creat și Instalat](#2-skills-custom-de-creat-și-instalat)
3. [Ordinea de Instalare](#3-ordinea-de-instalare-recomandata)
4. [Structura Directoare Skills](#4-structura-directoare-skills)

---

## 1. Skills Existente (Deja Disponibile în Claude)

Acestea sunt skills care există deja în `/mnt/skills/` și pe care le vom folosi direct:

| Skill | Locație | Utilizare în Proiect |
|-------|---------|---------------------|
| **docx** | `/mnt/skills/public/docx/` | Generare Lebenslauf, Bewerbungsschreiben, Deckblatt ca .docx |
| **pdf** | `/mnt/skills/public/pdf/` | Export PDF-uri CV, facturi, Bewerbungsmappe combinată |
| **frontend-design** | `/mnt/skills/public/frontend-design/` | Landing pages, dashboard UI, editor interface |
| **xlsx** | `/mnt/skills/public/xlsx/` | Export date admin, rapoarte financiare, analytics |
| **pptx** | `/mnt/skills/public/pptx/` | Prezentări pitch deck, investor materials |
| **skill-creator** | `/mnt/skills/examples/skill-creator/` | Creare și iterare pe skills custom |
| **web-artifacts-builder** | `/mnt/skills/examples/web-artifacts-builder/` | Componente React complexe (editor CV, dashboard) |
| **theme-factory** | `/mnt/skills/examples/theme-factory/` | Teme vizuale consistente cross-platform |
| **mcp-builder** | `/mnt/skills/examples/mcp-builder/` | MCP servers pentru integrări externe |
| **canvas-design** | `/mnt/skills/examples/canvas-design/` | Design-uri vizuale (template previews, social media assets) |

---

## 2. Skills Custom de Creat și Instalat

Acestea sunt skills-urile **noi** care trebuie create specific pentru proiect. Fiecare skill de mai jos include: numele, descrierea (trigger), structura fișierelor, și conținutul SKILL.md pe care trebuie să-l creezi.

---

### SKILL 2.1: `django-lebenslauf-core`

**Scop:** Scheletul Django al întregului proiect — structura de apps, models, settings, URL routing, middleware custom.

**Trigger:** Orice referință la setup Django, structura proiectului, models, migrations, settings, configurare inițială.

```
django-lebenslauf-core/
├── SKILL.md
├── templates/
│   ├── project_structure.txt        # Arborele complet de directoare
│   ├── settings_base.py.template    # Settings cu DSGVO config
│   ├── settings_production.py.template
│   ├── urls.py.template             # URL routing principal
│   └── docker-compose.yml.template  # Docker setup cu PostgreSQL + Redis
├── models/
│   ├── user_models.py.template      # User + UserProfile cu câmpuri DE
│   ├── document_models.py.template  # Document, Template, Section
│   ├── payment_models.py.template   # Subscription, Payment, Invoice
│   └── legal_models.py.template     # CookieConsent, GDPRRequest, AuditLog
└── middleware/
    ├── gdpr_middleware.py.template   # Cookie consent check middleware
    └── language_middleware.py.template # DE/EN language detection
```

**SKILL.md conținut cheie:**

```markdown
---
name: django-lebenslauf-core
description: >
  Core Django project structure for the Lebenslauf-Builder SaaS platform targeting
  the German job market. Use this skill whenever setting up the Django project,
  creating or modifying models, configuring settings, setting up Docker, or
  establishing the multi-app architecture. Triggers on: Django setup, project
  structure, models, migrations, database schema, settings configuration,
  Docker setup, or any foundational backend work for the Lebenslauf platform.
---

# Django Lebenslauf Core

## Project Structure

The platform uses a multi-app Django architecture:

### Apps
- `accounts/` - User auth, profile, DSGVO consent management
- `documents/` - Lebenslauf, Bewerbungsschreiben, Deckblatt, Templates
- `payments/` - Stripe integration, subscriptions, invoices (GoBD compliant)
- `editor/` - HTMX-powered CV editor with live preview
- `blog/` - Karriere-Blog with SEO (django-meta)
- `legal/` - Impressum, Datenschutz, AGB, Cookie Policy, Widerrufsbelehrung
- `api/` - DRF endpoints for editor AJAX, webhooks
- `dashboard/` - Mein Bereich user dashboard + Admin dashboard
- `automation/` - Celery tasks, n8n webhook receivers

### Database Design Principles
- PostgreSQL with JSONField for CV content (flexible schema)
- UUID primary keys on all user-facing models
- Soft delete with `deleted_at` timestamp (DSGVO audit trail)
- All timestamps in UTC, displayed in Europe/Berlin
- Encrypted fields for sensitive data (django-encrypted-model-fields)

### Key Settings
- LANGUAGE_CODE = 'de'
- TIME_ZONE = 'Europe/Berlin'
- USE_L10N = True (German number/date formatting)
- SECURE_SSL_REDIRECT = True
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- CSP headers via django-csp
- CORS restricted to own domain only
```

---

### SKILL 2.2: `htmx-editor-components`

**Scop:** Componente HTMX pentru editorul de CV — formulare dinamice, live preview, drag & drop secțiuni, upload foto.

**Trigger:** Editor CV, HTMX components, live preview, drag & drop, formulare dinamice, partial updates.

```
htmx-editor-components/
├── SKILL.md
├── templates/
│   ├── editor_base.html.template        # Layout editor cu sidebar + preview
│   ├── section_form.html.template       # Partial HTMX pentru o secțiune CV
│   ├── photo_upload.html.template       # Upload + crop foto cu progress bar
│   ├── live_preview.html.template       # Preview PDF/HTML real-time
│   ├── template_selector.html.template  # Grid template-uri cu preview
│   └── bewerbungsmappe.html.template    # Drag & drop document ordering
├── views/
│   ├── editor_views.py.template         # HTMX partial views
│   └── preview_views.py.template        # PDF generation endpoint
└── static/
    ├── editor.js.template               # Alpine.js + HTMX coordination
    └── editor.css.template              # Editor-specific styles
```

**SKILL.md conținut cheie:**

```markdown
---
name: htmx-editor-components
description: >
  HTMX-powered CV editor components for the Lebenslauf-Builder platform. Use
  this skill when building the interactive editor interface, implementing live
  preview, creating dynamic form sections, building drag & drop functionality,
  or any frontend component that uses HTMX partial page updates. Triggers on:
  editor UI, HTMX partials, live preview, dynamic forms, section management,
  photo upload, template switching, drag and drop, bewerbungsmappe builder,
  or any interactive frontend component of the platform.
---

# HTMX Editor Components

## Architecture
- Server-side rendering with Django templates
- HTMX for partial page updates (no full page reloads)
- Alpine.js for client-side state (form validation, UI toggles)
- WeasyPrint for HTML-to-PDF conversion
- Sortable.js (via CDN) for drag & drop

## Key Patterns

### Section CRUD via HTMX
- hx-post for adding new sections (Berufserfahrung, Ausbildung, etc.)
- hx-put for inline editing with autosave (debounced 500ms)
- hx-delete with confirmation modal
- hx-swap="outerHTML" for replacing section partials
- hx-trigger="keyup changed delay:500ms" for live preview updates

### Live Preview
- Dedicated iframe or shadow DOM showing rendered CV
- hx-trigger on any content change → server renders HTML preview
- Lazy PDF generation only on explicit "Download" click
- Template switching via hx-get swaps entire preview

### Lebenslauf-specific Sections
- Persönliche Daten (cu foto upload, Geburtsdatum, Familienstand)
- Berufserfahrung (sortable, repeatable)
- Ausbildung (sortable, repeatable)
- Kenntnisse (skill bars cu rating: Grundkenntnisse → Experte)
- Sprachen (CEFR levels A1-C2, Muttersprache option)
- Weiterbildungen, Ehrenamt, Interessen
- Unterschrift (Ort + Datum digital signature)

### Photo Upload
- Drag & drop zone cu progress indicator
- Client-side crop (Cropper.js via CDN)
- Server-side resize + optimization (Pillow)
- HTMX progress: hx-indicator for upload spinner
```

---

### SKILL 2.3: `german-legal-compliance`

**Scop:** Tot ce ține de conformitate legală germană — Impressum, DSGVO, Cookie Consent, AGB, Widerrufsbelehrung, facturare GoBD.

**Trigger:** Orice referință la legal, DSGVO, GDPR, Impressum, cookie consent, AGB, privacy policy, Widerrufsrecht, facturi.

```
german-legal-compliance/
├── SKILL.md
├── templates/
│   ├── impressum.html.template              # Template Impressum conform TMG §5
│   ├── datenschutzerklaerung.html.template   # Privacy Policy complet DE
│   ├── agb.html.template                     # Terms & Conditions DE
│   ├── cookie_banner.html.template           # 3-layer cookie consent TTDSG
│   ├── cookie_settings.html.template         # Granular cookie preferences
│   ├── widerrufsbelehrung.html.template      # Drept retragere 14 zile
│   ├── widerruf_formular.html.template       # Formular model retragere
│   └── rechnung.html.template                # Factură PDF conformă GoBD
├── models/
│   ├── consent_models.py.template            # CookieConsent, ConsentLog
│   ├── gdpr_models.py.template               # GDPRRequest, AuditLog, DataExport
│   └── invoice_models.py.template            # Invoice cu MwSt, GoBD fields
├── middleware/
│   └── cookie_consent_middleware.py.template  # Block tracking pre-consent
├── views/
│   ├── cookie_views.py.template              # HTMX cookie consent endpoints
│   ├── gdpr_views.py.template                # Data export, deletion, portability
│   └── legal_views.py.template               # Static legal pages
└── management/
    └── commands/
        ├── gdpr_cleanup.py.template          # Cron: delete expired data
        └── consent_audit.py.template         # Generate consent audit report
```

**SKILL.md conținut cheie:**

```markdown
---
name: german-legal-compliance
description: >
  Complete German legal compliance framework for SaaS platforms. Covers DSGVO
  (GDPR), BDSG, TTDSG cookie consent, Impressum (TMG §5 DDG), AGB, 
  Widerrufsbelehrung, and GoBD-compliant invoicing. Use this skill whenever
  implementing ANY legal page, cookie consent banner, GDPR data handling,
  privacy policy, terms of service, invoicing, or data protection feature.
  Also triggers on: Datenschutz, Impressum, cookie banner, consent management,
  data deletion, data export, Widerrufsrecht, Rechnung, MwSt, audit log,
  or any compliance-related implementation for the German market.
  CRITICAL: Always use this skill before creating any legal page or
  data handling feature — German law imposes severe penalties for non-compliance.
---

# German Legal Compliance Framework

## Legal Documents Required (Minimum Viable Legal)

### 1. Impressum (MANDATORY - TMG §5 / DDG Art. 5)
- Must be accessible within 2 clicks from ANY page
- Link labeled "Impressum" in footer on EVERY page
- Fine up to €50,000 for missing/incomplete Impressum
- Must include: full company name + legal form, physical address (no PO box),
  email + second contact method, Handelsregister number + Amtsgericht,
  USt-IdNr., Steuernummer, Geschäftsführer name
- Separate page from Datenschutzerklärung

### 2. Datenschutzerklärung (MANDATORY - Art. 13/14 DSGVO)
- In German language, accessible from every page
- Must list EVERY data processing activity with:
  - Purpose (Zweck), Legal basis (Rechtsgrundlage Art. 6 DSGVO),
  - Recipients (Empfänger), Retention period (Speicherdauer),
  - Third country transfers (Drittlandtransfer) with mechanism
- All cookies listed individually with: Name, Provider, Purpose, Duration, Type
- User rights section (Betroffenenrechte): Art. 15-22 DSGVO
- Right to complain to supervisory authority (Beschwerderecht)

### 3. Cookie Consent Banner (MANDATORY - TTDSG §25)
**Layer 1 (Initial Banner):**
- 3 equal buttons: "Alle akzeptieren" | "Einstellungen" | "Nur notwendige"
- NO pre-checked non-essential cookies
- NO "X" close button without choice
- Must block ALL tracking before consent

**Layer 2 (Settings):**
- Individual toggles per category:
  - Notwendig (always ON, disabled toggle)
  - Statistik (OFF default)
  - Marketing (OFF default)  
  - Externe Medien (OFF default)
- Cookie list under each category

**Layer 3 (Details):**
- Full cookie table: Name | Anbieter | Zweck | Ablauf | Typ

### 4. AGB (MANDATORY for commercial sites - §312d BGB)
- Same language as website
- Prices MUST include MwSt (PAngV)
- ODR link mandatory: https://ec.europa.eu/consumers/odr

### 5. Widerrufsbelehrung (MANDATORY - §312g BGB)
- 14 calendar days withdrawal right
- Model withdrawal form available for download
- Must be shown BEFORE payment completion
- Checkbox confirmation required at checkout

### 6. Rechnungen / Invoices (GoBD compliant)
- Sequential invoice numbers (no gaps)
- Net price + MwSt rate (19%) + MwSt amount + gross price
- Company details: name, address, Steuernummer, USt-IdNr.
- 10-year retention obligation (Aufbewahrungspflicht)

## Cookie Consent Technical Implementation
- Server-side middleware blocks tracking scripts pre-consent
- Consent stored in first-party cookie + database for authenticated users
- All third-party scripts loaded conditionally via HTMX hx-trigger
- Google Fonts MUST be self-hosted (Landgericht München ruling)
- YouTube embeds: thumbnail + click-to-load with consent check
- Consent log: UUID, timestamp, IP (hashed), user_agent, banner_version, choices

## DSGVO User Rights Implementation
- Art. 15 Auskunftsrecht: Data access endpoint → JSON response
- Art. 17 Recht auf Löschung: Soft delete → hard delete after 30 days
- Art. 20 Datenübertragbarkeit: Export as JSON + PDF ZIP download
- All requests logged in AuditLog with timestamp and action type
- Automated confirmation emails for all GDPR requests
```

---

### SKILL 2.4: `stripe-payment-de`

**Scop:** Integrare completă Stripe pentru piața germană — checkout, webhooks, SEPA, facturare, Widerrufsrecht.

**Trigger:** Plăți, Stripe, checkout, subscription, factură, SEPA, Giropay, pricing, MwSt.

```
stripe-payment-de/
├── SKILL.md
├── templates/
│   ├── pricing_page.html.template       # Pricing cu MwSt inclus (PAngV)
│   ├── checkout.html.template           # Stripe Elements + legal checkboxes
│   ├── payment_success.html.template    # Confirmare + factura
│   ├── payment_cancel.html.template     # Cancel page
│   └── subscription_manage.html.template # Dashboard subscripție
├── views/
│   ├── checkout_views.py.template       # Stripe Checkout Session creation
│   ├── webhook_views.py.template        # Stripe webhook handler
│   └── subscription_views.py.template   # Manage, cancel, refund
├── services/
│   ├── stripe_service.py.template       # Stripe API wrapper
│   └── invoice_service.py.template      # GoBD invoice PDF generation
└── tasks/
    ├── payment_tasks.py.template        # Celery: process webhooks async
    └── reminder_tasks.py.template       # Celery: expiration reminders
```

**SKILL.md conținut cheie:**

```markdown
---
name: stripe-payment-de
description: >
  Stripe payment integration optimized for the German market with SEPA,
  Giropay, Sofort, MwSt handling, GoBD-compliant invoicing, and 14-day
  Widerrufsrecht implementation. Use this skill for ANY payment-related
  feature: pricing page, checkout flow, webhook handling, subscription
  management, invoice generation, refund processing, or payment method
  configuration. Triggers on: payment, Stripe, checkout, subscription,
  pricing, MwSt, Rechnung, invoice, SEPA, Giropay, Widerrufsrecht, refund,
  billing, or any financial transaction on the platform.
---

# Stripe Payment Integration (German Market)

## Payment Methods (Priority Order for DE)
1. Kreditkarte (Visa/Mastercard) - via Stripe Elements
2. PayPal - via Stripe PayPal integration
3. SEPA-Lastschrift - via Stripe SEPA Direct Debit
4. Sofortüberweisung/Klarna - via Stripe Sofort
5. Giropay - via Stripe Giropay
6. Apple Pay / Google Pay - via Stripe Payment Request Button

## Pricing Rules (PAngV - Preisangabenverordnung)
- ALL prices shown to consumers MUST include MwSt (19%)
- Display format: "17,99 € inkl. MwSt" (German comma decimal)
- Net price + MwSt breakdown shown at checkout
- Currency: EUR only

## Checkout Flow
1. User selects plan on /preise/ page
2. HTMX modal with Stripe Elements embedded
3. Legal checkboxes BEFORE payment button:
   - [ ] Ich habe die AGB gelesen und akzeptiere diese
   - [ ] Ich habe die Widerrufsbelehrung zur Kenntnis genommen
   - [ ] Ich stimme zu, dass die Dienstleistung sofort beginnt (Widerruf-Ausnahme)
4. Stripe Checkout Session with payment_intent
5. Webhook: payment_intent.succeeded → activate subscription
6. Redirect to success page + send confirmation email + invoice PDF

## Widerrufsrecht (14-day withdrawal)
- Timer starts at payment completion
- Dashboard shows "Widerruf einreichen" button during 14-day window
- Automated refund via Stripe Refund API
- Email confirmation of withdrawal receipt
- Plan deactivated immediately upon refund

## Invoice Generation (GoBD)
- Triggered by successful payment webhook
- Sequential Rechnungsnummer (format: RE-2026-00001)
- PDF generated via WeasyPrint with company letterhead
- Fields: Rechnungsnummer, Rechnungsdatum, Leistungszeitraum,
  Nettobetrag, MwSt-Satz (19%), MwSt-Betrag, Bruttobetrag
- Stored 10 years (Aufbewahrungspflicht AO §147)
- Available for download in user dashboard
```

---

### SKILL 2.5: `dashboard-htmx`

**Scop:** Dashboard-uri complete — user dashboard (Mein Bereich), subscription management, admin panel.

**Trigger:** Dashboard, Mein Bereich, admin panel, document management, user settings, analytics.

```
dashboard-htmx/
├── SKILL.md
├── templates/
│   ├── dashboard_base.html.template       # Layout cu sidebar navigation
│   ├── meine_dokumente.html.template      # Document grid/list view
│   ├── document_card.html.template        # HTMX partial: single document card
│   ├── konto.html.template                # Account settings
│   ├── abo_zahlung.html.template          # Subscription & payment history
│   ├── datenschutz_settings.html.template # DSGVO user controls
│   ├── bewerbungsmappe.html.template      # Application folder builder
│   └── admin/
│       ├── admin_dashboard.html.template  # Revenue + user metrics
│       ├── user_management.html.template  # User list with filters
│       ├── gdpr_panel.html.template       # DSGVO requests management
│       └── content_management.html.template
├── views/
│   ├── dashboard_views.py.template
│   ├── document_views.py.template
│   └── admin_views.py.template
└── static/
    └── dashboard.js.template              # Alpine.js dashboard interactions
```

**SKILL.md conținut cheie:**

```markdown
---
name: dashboard-htmx
description: >
  HTMX-powered dashboards for the Lebenslauf-Builder platform including user
  dashboard (Mein Bereich), document management, subscription controls, DSGVO
  settings, and admin panel with revenue analytics. Use this skill for any
  dashboard page, user settings interface, document management view, admin
  panel, or analytics display. Triggers on: dashboard, Mein Bereich, Konto,
  document list, user settings, admin panel, analytics, revenue metrics,
  GDPR management panel, Bewerbungsmappe, or any authenticated user interface.
---

# Dashboard Components

## User Dashboard (Mein Bereich)

### Sidebar Navigation
- Meine Dokumente (active by default)
- Neue Vorlage wählen
- Bewerbungsmappe
- Konto-Einstellungen
- Abo & Zahlung
- Datenschutz
- Hilfe & Support

### Meine Dokumente
- Grid view (default) / List view toggle via Alpine.js
- Document cards: thumbnail + title + type badge + last edited + actions
- Actions dropdown (HTMX): Bearbeiten, Duplizieren, Herunterladen, Löschen
- Premium lock overlay on documents with premium features (free users)
- Filter by doc_type (Lebenslauf | Anschreiben | Deckblatt)
- Sort by: Zuletzt bearbeitet | Name | Erstellt am
- Infinite scroll via hx-trigger="revealed"
- Empty state: illustration + "Erstellen Sie Ihren ersten Lebenslauf" CTA

### Bewerbungsmappe
- Drag & drop document ordering (Sortable.js)
- Combine: Deckblatt + Lebenslauf + Anschreiben → single PDF
- Optional: attach Zeugnisse (uploaded PDFs)
- Export: combined PDF or ZIP with separate files
- Save as named Bewerbungsmappe for reuse

## Admin Dashboard
- Revenue: MRR, ARR, conversion rate, churn rate (Recharts graphs)
- Users: total, active, premium, new this month
- Documents: created today/week/month, popular templates
- DSGVO Panel: pending deletion requests, pending export requests, audit log
```

---

### SKILL 2.6: `karriere-blog-seo`

**Scop:** Blog engine SEO-optimizat pentru piața germană — articole, categorii, structured data, sitemap, meta tags.

**Trigger:** Blog, SEO, articol, keyword, sitemap, meta tags, structured data, Schema.org.

```
karriere-blog-seo/
├── SKILL.md
├── templates/
│   ├── blog_list.html.template          # Blog listing cu pagination
│   ├── blog_detail.html.template        # Article page cu structured data
│   ├── blog_category.html.template      # Category archive
│   ├── blog_sidebar.html.template       # Related articles, CTA widget
│   └── seo/
│       ├── meta_tags.html.template      # Dynamic meta + OG + Twitter Cards
│       ├── structured_data.html.template # JSON-LD templates
│       └── sitemap.xml.template         # Dynamic XML sitemap
├── models/
│   ├── blog_models.py.template          # Article, Category, Tag, Author
│   └── seo_models.py.template           # SEOMixin, MetaTag overrides
├── views/
│   └── blog_views.py.template           # ListView, DetailView, feed
└── management/
    └── commands/
        └── generate_sitemap.py.template # Celery-triggered sitemap regen
```

**SKILL.md conținut cheie:**

```markdown
---
name: karriere-blog-seo
description: >
  SEO-optimized career blog engine for the German job market. Handles blog
  articles, categories, structured data (Schema.org), XML sitemaps, meta tags,
  Open Graph, and German keyword optimization. Use this skill for any blog
  feature, SEO implementation, content strategy, sitemap generation, meta tag
  configuration, structured data markup, or search engine optimization task.
  Triggers on: blog, Karriere-Blog, SEO, article, sitemap, meta tags,
  structured data, Schema.org, keywords, Open Graph, canonical URLs,
  breadcrumbs, or any content marketing feature.
---

# Karriere-Blog & SEO Engine

## URL Structure (German-optimized)
- /karriere-blog/ → Blog index
- /karriere-blog/lebenslauf-schreiben/ → Article (slug from title)
- /karriere-blog/kategorie/bewerbungstipps/ → Category
- /karriere-blog/tag/vorstellungsgespraech/ → Tag

## SEO Features
- django-meta for per-page meta tag management
- Auto-generated meta description from first 160 chars
- Canonical URLs on all pages
- hreflang tags for DE/EN versions
- XML sitemap with lastmod, changefreq, priority
- robots.txt with sitemap reference
- Breadcrumb navigation (BreadcrumbList schema)

## Structured Data (JSON-LD)
- Organization: homepage
- Product + Offer: pricing page (with MwSt priceSpecification)
- FAQPage: pricing FAQ, homepage FAQ
- BlogPosting: each article (author, datePublished, image)
- HowTo: tutorial articles (Wie schreibt man einen Lebenslauf)
- BreadcrumbList: all pages
- AggregateRating: from Trustpilot/ProvenExpert widget

## Target Keywords (Primary)
- Lebenslauf Vorlage (90.500/mo)
- Lebenslauf erstellen (49.500/mo)
- Bewerbungsschreiben Muster (33.100/mo)
- tabellarischer Lebenslauf (27.100/mo)
- CV erstellen kostenlos (22.200/mo)

## Content Strategy
- 1 pillar article per main keyword (2000+ words)
- 5-10 cluster articles linking to pillar
- Internal linking strategy between blog ↔ templates ↔ editor
- CTA widgets in sidebar and inline (template preview + "Jetzt erstellen")
```

---

### SKILL 2.7: `n8n-automation-workflows`

**Scop:** Automatizări n8n + Celery — email flows, webhook processing, DSGVO automation, notifications.

**Trigger:** Automatizare, n8n, webhook, Celery, email flow, notification, cron job, background task.

```
n8n-automation-workflows/
├── SKILL.md
├── workflows/
│   ├── welcome_email.json.template        # n8n: registration → welcome email
│   ├── payment_confirmation.json.template # n8n: Stripe webhook → email + invoice
│   ├── subscription_expiring.json.template # n8n: cron → check expiring → email
│   ├── gdpr_deletion.json.template        # n8n: deletion request → process → confirm
│   └── gdpr_export.json.template          # n8n: export request → generate → email link
├── views/
│   └── webhook_views.py.template          # Django webhook endpoints for n8n
├── tasks/
│   ├── email_tasks.py.template            # Celery email dispatch
│   ├── pdf_tasks.py.template              # Celery PDF generation
│   ├── gdpr_tasks.py.template             # Celery GDPR processing
│   └── maintenance_tasks.py.template      # Celery cleanup, sitemap regen
└── signals/
    └── automation_signals.py.template     # Django signals → trigger workflows
```

**SKILL.md conținut cheie:**

```markdown
---
name: n8n-automation-workflows
description: >
  Automation workflows using n8n (self-hosted) and Django Celery for the
  Lebenslauf-Builder platform. Covers email automation, webhook processing,
  DSGVO compliance automation, payment notifications, and background task
  management. Use this skill for any automation, workflow, webhook endpoint,
  Celery task, email flow, cron job, or background processing feature.
  Triggers on: automation, n8n, webhook, Celery, email flow, background task,
  cron, notification, workflow, signal, or any async processing need.
---

# Automation & Workflow Engine

## Architecture
- n8n (self-hosted on same Hetzner server) for visual workflow orchestration
- Django Celery + Redis for background task queue
- Django signals for event-driven triggers
- Webhook endpoints for n8n ↔ Django communication

## Webhook Endpoints (Django → n8n)
| Endpoint | Trigger | n8n Action |
|----------|---------|------------|
| POST /webhooks/stripe/ | Stripe events | Route by event type |
| POST /webhooks/user-registered/ | New account | Welcome email flow |
| POST /webhooks/document-created/ | Doc finished | Analytics + AI suggestions |
| POST /webhooks/subscription-expiring/ | Celery cron | Reminder email |
| POST /webhooks/gdpr-deletion/ | User request | Anonymize + delete + confirm |
| POST /webhooks/gdpr-export/ | User request | Generate ZIP + email link |

## Celery Tasks
- `generate_pdf`: Async PDF rendering (WeasyPrint)
- `send_email`: Transactional email via AWS SES
- `generate_invoice_pdf`: GoBD invoice generation
- `process_gdpr_deletion`: Cascade delete + audit log
- `process_gdpr_export`: Compile all user data → ZIP
- `regenerate_sitemap`: Triggered on blog/template publish
- `cleanup_expired_data`: Daily cron, remove data past retention

## Security
- All webhook endpoints require HMAC signature verification
- Stripe webhooks verified with stripe.Webhook.construct_event()
- n8n webhooks use shared secret in Authorization header
- Rate limiting on all webhook endpoints (django-ratelimit)
- IP allowlist for n8n server communication
```

---

### SKILL 2.8: `lebenslauf-templates`

**Scop:** Sistem de template-uri pentru Lebenslauf german — design, rendering HTML→PDF, customization.

**Trigger:** Template CV, Lebenslauf Vorlage, design template, PDF rendering, WeasyPrint.

```
lebenslauf-templates/
├── SKILL.md
├── templates/
│   ├── klassisch.html.template         # Template clasic german (tabelar)
│   ├── modern.html.template            # Template modern cu sidebar
│   ├── kreativ.html.template           # Template creativ
│   ├── akademisch.html.template        # CV academic multi-pagină
│   ├── it_tech.html.template           # Template IT cu skill bars
│   ├── bewerbungsschreiben.html.template # Cover letter template
│   ├── deckblatt.html.template         # Application cover page
│   └── _base_template.html.template    # Base rendering engine
├── styles/
│   ├── base.css.template               # Shared print + screen styles
│   └── themes.css.template             # Color themes (74 variante)
├── rendering/
│   ├── pdf_renderer.py.template        # WeasyPrint HTML → PDF
│   └── preview_renderer.py.template    # HTML preview for editor
└── models/
    └── template_models.py.template     # Template, TemplateCategory, Theme
```

**SKILL.md conținut cheie:**

```markdown
---
name: lebenslauf-templates
description: >
  Template system for German Lebenslauf (CV), Bewerbungsschreiben (cover letter),
  and Deckblatt (cover page) with HTML-to-PDF rendering via WeasyPrint. Use this
  skill when creating, modifying, or rendering CV templates, designing new template
  layouts, implementing PDF generation, or managing the template catalog. Triggers on:
  template, Vorlage, Lebenslauf design, PDF rendering, WeasyPrint, template catalog,
  print styles, cover letter template, Deckblatt, or any document design task.
  Also use when the user wants to customize colors, fonts, layouts, or add new
  template categories.
---

# Lebenslauf Template System

## German CV Specifics (vs. International)
- Photo slot (top-right or centered) — standard in Germany
- Persönliche Daten section with: Geburtsdatum, Geburtsort, 
  Staatsangehörigkeit, Familienstand
- Chronological order: newest first (anti-chronologisch)
- Unterschrift line at bottom (Ort, Datum)
- Tabellarisch (tabular) format is the most common
- Professional, conservative design preferred for most industries
- A4 format (210mm × 297mm), not US Letter

## Template Categories
1. Klassisch — tabular, formal, conservative industries
2. Modern — clean sidebar, subtle colors, tech/startup
3. Kreativ — bold design, creative industries
4. Akademisch — multi-page CV for researchers/academics
5. IT/Tech — skill bars, project showcase
6. Student — education-focused, minimal experience
7. Pflege/Handwerk — industry-specific sections

## Rendering Pipeline
1. User content (JSON) + Template (HTML/CSS) + Theme (colors/fonts)
2. Django template engine renders to full HTML
3. Screen preview: served as HTML in editor iframe
4. PDF export: WeasyPrint renders HTML → PDF (A4, print CSS)
5. PDF cached in FileField, invalidated on content/style change

## Customization Options
- Free: 3 fonts, 30 color themes, predefined layout
- Premium: 12 fonts, 74 color themes, custom layout reorder,
  creative backgrounds, picture styles, rating styles, 
  specialized sections, up to 10 pages
```

---

### SKILL 2.9: `deployment-hetzner`

**Scop:** Deployment complet pe Hetzner Cloud — Docker, Nginx, SSL, CI/CD, monitoring.

**Trigger:** Deployment, Hetzner, Docker, Nginx, SSL, CI/CD, production, server setup, monitoring.

```
deployment-hetzner/
├── SKILL.md
├── docker/
│   ├── Dockerfile.template              # Django production image
│   ├── Dockerfile.n8n.template          # n8n self-hosted
│   ├── docker-compose.prod.yml.template # Full production stack
│   └── .env.example.template            # Environment variables
├── nginx/
│   ├── nginx.conf.template              # Nginx reverse proxy + SSL
│   └── security_headers.conf.template   # CSP, HSTS, X-Frame-Options
├── scripts/
│   ├── deploy.sh.template               # Zero-downtime deploy script
│   ├── backup.sh.template               # PostgreSQL + media backup
│   └── ssl_renew.sh.template            # Let's Encrypt renewal
└── monitoring/
    ├── prometheus.yml.template           # Metrics collection
    └── alerting_rules.yml.template       # Alert rules (uptime, errors, disk)
```

---

## 3. Ordinea de Instalare Recomandată

Instalarea trebuie făcută în această ordine (dependențe):

| Pas | Skill | Depinde de | Motiv |
|-----|-------|-----------|-------|
| 1 | `django-lebenslauf-core` | — | Fundația: models, settings, project structure |
| 2 | `german-legal-compliance` | Core | Legal trebuie integrat de la început |
| 3 | `lebenslauf-templates` | Core | Templates sunt necesare pentru editor |
| 4 | `htmx-editor-components` | Core + Templates | Editorul consumă templates |
| 5 | `stripe-payment-de` | Core + Legal | Plăți necesită Widerrufsbelehrung |
| 6 | `dashboard-htmx` | Core + Editor + Payments | Dashboard-ul leagă totul |
| 7 | `karriere-blog-seo` | Core | Independent, poate fi paralel |
| 8 | `n8n-automation-workflows` | Core + Payments + Legal | Automatizează flows existente |
| 9 | `deployment-hetzner` | Toate | Final: deploy ce e construit |

### Flux de instalare:

```
Pasul 1: django-lebenslauf-core
    ↓
Pasul 2: german-legal-compliance ←── CRITIC: fără asta nu lansăm
    ↓
Pasul 3: lebenslauf-templates
    ↓
Pasul 4: htmx-editor-components ←── Core product
    ↓
Pasul 5: stripe-payment-de ←── Monetizare
    ↓
Pasul 6: dashboard-htmx ←── User experience
    ↓
Pasul 7: karriere-blog-seo ←── Growth engine (poate fi paralel cu 5-6)
    ↓
Pasul 8: n8n-automation-workflows ←── Operațional
    ↓
Pasul 9: deployment-hetzner ←── Production launch
```

---

## 4. Structura Directoare Skills

Toate skills-urile custom se instalează în `/mnt/skills/user/`:

```
/mnt/skills/user/
├── django-lebenslauf-core/
│   ├── SKILL.md
│   ├── templates/
│   ├── models/
│   └── middleware/
├── htmx-editor-components/
│   ├── SKILL.md
│   ├── templates/
│   ├── views/
│   └── static/
├── german-legal-compliance/
│   ├── SKILL.md
│   ├── templates/
│   ├── models/
│   ├── middleware/
│   ├── views/
│   └── management/
├── stripe-payment-de/
│   ├── SKILL.md
│   ├── templates/
│   ├── views/
│   ├── services/
│   └── tasks/
├── dashboard-htmx/
│   ├── SKILL.md
│   ├── templates/
│   ├── views/
│   └── static/
├── karriere-blog-seo/
│   ├── SKILL.md
│   ├── templates/
│   ├── models/
│   ├── views/
│   └── management/
├── n8n-automation-workflows/
│   ├── SKILL.md
│   ├── workflows/
│   ├── views/
│   ├── tasks/
│   └── signals/
└── deployment-hetzner/
    ├── SKILL.md
    ├── docker/
    ├── nginx/
    ├── scripts/
    └── monitoring/
```

---

## Note Importante

1. **Skill-urile existente** (docx, pdf, frontend-design, etc.) se folosesc **în combinație** cu cele custom. De exemplu, `lebenslauf-templates` va folosi skill-ul `pdf` pentru rendering, iar `dashboard-htmx` va folosi `frontend-design` pentru UI.

2. **Fiecare SKILL.md** trebuie creat cu frontmatter YAML valid (`name` + `description`) — description-ul este mecanismul principal de triggering.

3. **Fișierele .template** din fiecare skill sunt templates de cod pe care Claude le va folosi ca referință și punct de plecare atunci când generează codul efectiv. Nu sunt cod executabil direct.

4. **german-legal-compliance** este cel mai critic skill — fără el, site-ul nu poate fi lansat legal în Germania. Amenzile DSGVO pot ajunge la 4% din cifra de afaceri anuală sau 20 milioane EUR.

5. **Testare recomandată:** După crearea fiecărui skill, folosește `skill-creator` pentru a rula evaluări și a verifica triggeringul corect.