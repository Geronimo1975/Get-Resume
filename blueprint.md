Read platform-analysis.mdThought for 9sThis is a substantial architectural planning document. Let me produce the comprehensive blueprint you need across all five dimensions.

---

# Complete Technical & Product Blueprint: German Resume Platform (NovoResume Clone)

## 1. Platform Analysis — NovoResume Reverse-Engineering

### Frontend Architecture (Inferred)

**Routing & SPA Structure:**
NovoResume operates as a single-page application with route-based code splitting. Key routes include:

| Route | Purpose
|-----|-----
| `/` | Marketing landing + CTA
| `/resume-templates` | Template gallery with filtering
| `/editor/:resumeId` | Core resume editor
| `/dashboard` | User resume management
| `/account` | Subscription & billing
| `/cover-letter` | Anschreiben builder


**Resume Editor — Core Component:**
The editor is the product's centerpiece. It uses:

- **Two-panel layout**: Left = form-based input sections (drag-to-reorder), Right = real-time WYSIWYG preview rendered as a scaled-down page
- **Section-based architecture**: Each resume section (Experience, Education, Skills) is an independent component with its own schema, validation, and drag handle
- **Drag-and-drop**: Likely built on a library like `SortableJS` or `dnd-kit` — sections and items within sections are reorderable
- **Real-time preview**: The right panel re-renders on every input change via reactive state binding. The preview is HTML/CSS rendered at A4 proportions (210mm × 297mm), scaled down via CSS `transform: scale()`
- **Template engine**: Templates are CSS-driven skins applied over a shared HTML structure. Switching templates changes the stylesheet, not the data model
- **Rich text**: Limited rich text (bold, italic, links, bullets) within description fields — likely a constrained contenteditable or a lightweight editor like Tiptap


**Template System:**

- Templates share a common data schema but differ in CSS layout, typography, color scheme, and section ordering
- Template metadata: `id`, `name`, `thumbnail`, `category`, `isPremium`, `colorSchemes[]`, `fontPairings[]`
- Color/font customization is parametric — users pick from curated options that inject CSS variables


### Backend Architecture (Inferred)

**Database Schema (Conceptual ERD):**

```plaintext
users
├── id (UUID, PK)
├── email (unique, indexed)
├── password_hash
├── name, avatar_url
├── subscription_tier (free | premium | lifetime)
├── subscription_expires_at
├── stripe_customer_id
├── created_at, updated_at
└── gdpr_consent_at, gdpr_consent_version

resumes
├── id (UUID, PK)
├── user_id (FK → users)
├── title
├── template_id (FK → templates)
├── content (JSONB) ← entire resume data
├── style_overrides (JSONB) ← color, font, spacing
├── language (de, en, etc.)
├── is_public (boolean)
├── created_at, updated_at
└── last_exported_at

templates
├── id (PK)
├── name, slug, thumbnail_url
├── category, is_premium
├── base_css, layout_config (JSONB)
├── supported_sections (JSONB)
└── sort_order, is_active

subscriptions
├── id (PK)
├── user_id (FK → users)
├── stripe_subscription_id
├── plan (monthly | annual | lifetime)
├── status (active | canceled | past_due)
├── current_period_start, current_period_end
└── canceled_at

cover_letters
├── id (UUID, PK)
├── user_id (FK → users)
├── resume_id (FK → resumes, nullable)
├── content (JSONB)
├── template_id (FK → templates)
└── created_at, updated_at
```

**Resume `content` JSONB structure:**

```json
{
  "personalInfo": {
    "firstName": "Max",
    "lastName": "Mustermann",
    "email": "...",
    "phone": "...",
    "address": "Berlin, Deutschland",
    "photo": "https://storage.../photo.jpg",
    "dateOfBirth": "1990-01-15",
    "nationality": "Deutsch",
    "maritalStatus": "Ledig"
  },
  "sections": [
    {
      "type": "experience",
      "title": "Berufserfahrung",
      "order": 1,
      "items": [
        {
          "id": "uuid",
          "title": "Senior Entwickler",
          "organization": "SAP SE",
          "location": "Walldorf",
          "startDate": "2020-03",
          "endDate": null,
          "current": true,
          "description": "<p>Led a team of...</p>"
        }
      ]
    },
    {
      "type": "education",
      "title": "Ausbildung",
      "order": 2,
      "items": [...]
    },
    {
      "type": "skills",
      "title": "Kenntnisse",
      "order": 3,
      "items": [...]
    }
  ],
  "sectionOrder": ["personalInfo", "experience", "education", "skills"]
}
```

**PDF Generation Pipeline:**

1. User clicks "Download PDF"
2. Backend receives request with `resumeId`
3. Server renders the resume HTML+CSS using the same template engine (server-side)
4. HTML → PDF via headless Chrome (Puppeteer/Playwright) or WeasyPrint (Python-native, ideal for Django)
5. PDF is streamed back or temporarily stored and served via signed URL
6. Free tier: watermark injected; Premium: clean export


**Feature Gating (Free vs. Premium):**

| Feature | Free | Premium
|-----|-----
| Resume count | 1 | Unlimited
| Templates | 3-4 basic | All (20+)
| PDF export | With watermark | Clean
| Color customization | Limited | Full palette
| Cover letter builder | No | Yes
| AI suggestions | No | Yes
| Custom sections | No | Yes
| Zeugnisse upload | No | Yes


---

## 2. German Market Adaptation

### CV/Lebenslauf Specifics

**German CV differs fundamentally from Anglo-American resumes:**

| Element | International | German Standard
|-----|-----
| Photo | Optional/discouraged | Expected (Bewerbungsfoto)
| Date of birth | Never | Standard
| Marital status | Never | Common
| Nationality | Rare | Common
| Chronological order | Reverse-chrono | Reverse-chrono (modern) or chrono (traditional)
| Handwritten signature | Never | Digital signature on Lebenslauf
| Zeugnisse | Not attached | Attached as package


**Required template formats:**

1. **Tabellarischer Lebenslauf** (standard tabular CV) — the dominant format in Germany
2. **Europass** — for EU mobility, required by some public-sector employers
3. **Moderner Lebenslauf** — design-forward, for creative/tech industries
4. **Ausführlicher Lebenslauf** — narrative form, sometimes requested for academic/legal roles


**Industry-specific templates:**

- **IT/Tech**: Skills-heavy, GitHub/portfolio links, project sections
- **Ingenieurwesen**: Certification sections, technical competencies matrix
- **Gesundheitswesen**: Approbation, Facharzttitel, continuing education (Fortbildungen)
- **Verwaltung/Öffentlicher Dienst**: Formal, conservative, Europass-compatible
- **Kaufmännisch**: Standard tabular, emphasis on Ausbildung


**Bewerbungsmappe (Application Package) Builder:**
German applications are not just a resume — they're a complete package:

1. **Anschreiben** (cover letter) — with formal German letter structure (DIN 5008)
2. **Deckblatt** (title page) — optional, with photo and key details
3. **Lebenslauf** — the CV itself
4. **Zeugnisse & Zertifikate** — uploaded PDFs of work references, degrees, certifications
5. **Combined PDF export** — merge all into one ordered PDF package


### B2B Layer Architecture

**Company/HR Accounts:**

```plaintext
organizations
├── id (UUID, PK)
├── name, slug
├── type (company | agency)
├── logo_url
├── plan (starter | professional | enterprise)
├── max_seats
├── billing_email
├── stripe_customer_id
└── created_at

org_members
├── id (PK)
├── org_id (FK → organizations)
├── user_id (FK → users)
├── role (owner | admin | recruiter | viewer)
└── invited_at, accepted_at

candidate_profiles (for agency use)
├── id (UUID, PK)
├── org_id (FK → organizations)
├── candidate_name, candidate_email
├── resume_id (FK → resumes, nullable)
├── status (new | reviewed | shortlisted | rejected | placed)
├── notes (TEXT)
├── tags (JSONB)
└── created_at, updated_at
```

**B2B Features:**

- **Multi-seat accounts**: Invite team members via email, role-based access
- **Candidate pipeline**: Kanban-style board for tracking candidates
- **Bulk resume review**: Grid view with quick-actions (star, reject, shortlist)
- **Resume standardization**: Agency uploads candidate resumes → platform reformats into consistent templates (white-label)
- **Analytics**: Hiring funnel metrics, time-to-fill, team activity
- **API access** (Enterprise): REST API for ATS integration


### Legal & Compliance Architecture

#### GDPR/DSGVO Compliance

**Data model additions:**

```plaintext
consent_records
├── id (PK)
├── user_id (FK → users)
├── consent_type (marketing | analytics | functional | necessary)
├── granted (boolean)
├── ip_address
├── user_agent
├── consent_version (string, e.g. "v2.1")
├── granted_at
└── revoked_at

gdpr_requests
├── id (PK)
├── user_id (FK → users)
├── request_type (access | erasure | portability | rectification)
├── status (pending | processing | completed | denied)
├── requested_at
├── completed_at
├── processed_by (FK → admin users)
└── notes
```

**Technical measures:**

- **Data minimization**: Only collect fields necessary for CV creation. Optional fields clearly marked
- **Right to erasure (Art. 17)**: One-click "Konto löschen" → soft delete (30-day grace) → hard delete cascade (user, resumes, files, consent records, payment data anonymization)
- **Data portability (Art. 20)**: Export all user data as structured JSON + uploaded files as ZIP
- **Consent management**: Granular, per-purpose consent stored with timestamp and version
- **Data retention policy**: Auto-delete inactive accounts after 24 months with 30-day warning emails
- **Encryption**: AES-256 at rest, TLS 1.3 in transit, encrypted backups


#### Cookie Consent (IAB TCF 2.2 Compliant)

```plaintext
Cookie Categories:
├── Necessary (always on, no consent needed)
│   ├── Session cookies
│   ├── CSRF tokens
│   └── Cookie consent state
├── Functional (opt-in)
│   ├── Language preference
│   ├── Theme preference
│   └── Editor autosave
├── Analytics (opt-in)
│   ├── Matomo/Plausible (EU-hosted alternative to GA)
│   └── Error tracking (Sentry, EU instance)
└── Marketing (opt-in)
    ├── Retargeting pixels
    └── Attribution tracking
```

Implementation: Use a library like `cookie-consent-banner` or build a custom Vue component. Store consent state in a first-party cookie and replicate to `consent_records` table on authentication.

#### Impressum Auto-Generation

Required fields per § 5 TMG:

- Company name, legal form (GmbH, UG, etc.)
- Full address (no PO boxes)
- Contact: phone + email
- Handelsregister number + court
- Geschäftsführer name(s)
- USt-IdNr. (VAT ID)
- Responsible for content per § 55 RStV


Build as a settings form in admin → auto-renders at `/impressum`.

#### Datenschutzerklärung

Auto-generated from a template engine that takes:

- Company details (from Impressum)
- Active integrations (Stripe, analytics, etc.)
- Data processing purposes
- Third-party processors list
- Cookie categories


Rendered at `/datenschutz`, versioned, with change history.

### Payment System

**Provider: Stripe** (best ecosystem, supports all requirements)

| Feature | Implementation
|-----|-----
| SEPA Direct Debit | Stripe SEPA Debit payment method
| Credit/Debit cards | Stripe Elements
| PayPal | Stripe PayPal integration
| Sofortüberweisung | Stripe Sofort (Klarna)
| German invoicing | Stripe Invoicing with MwSt.
| Kleinunternehmerregelung | Toggle to suppress VAT on invoices (§ 19 UStG)
| Recurring billing | Stripe Subscriptions
| Cancellation | Must honor Fernabsatzgesetz: 14-day Widerrufsrecht, cancellation effective at period end


**Webhook architecture:**

```plaintext
Stripe → /api/webhooks/stripe/ (Django view)
├── customer.subscription.created → activate premium
├── customer.subscription.updated → sync plan changes
├── customer.subscription.deleted → downgrade to free
├── invoice.payment_succeeded → store invoice PDF
├── invoice.payment_failed → send dunning email
└── charge.refunded → handle refund logic
```

**Invoice requirements (German law):**

- Sequential invoice numbers
- Full company address (sender + recipient)
- Date + delivery date
- Net amount, VAT rate (19%), VAT amount, gross amount
- USt-IdNr.
- Payment method reference


---

## 3. Technical Stack Blueprint

### Architecture Overview

```plaintext
┌─────────────────────────────────────┐
│         Vue.js 3 SPA (Vite)         │
│  Pinia state │ Vue Router │ i18n    │
│  TipTap editor │ VueDraggable       │
└──────────────┬──────────────────────┘
               │ HTTPS (REST JSON)
               ▼
┌─────────────────────────────────────┐
│     Django 5.x + DRF (REST API)     │
│  JWT Auth │ Celery tasks │ Signals  │
│  WeasyPrint PDF │ django-storages   │
└──────┬───────────┬──────────────────┘
       │           │
       ▼           ▼
┌────────────┐ ┌──────────────────┐
│ PostgreSQL │ │  S3-compatible   │
│  15+ with  │ │  Object Storage  │
│   JSONB    │ │  (MinIO / AWS)   │
└────────────┘ └──────────────────┘
```

### Key Technology Decisions

| Decision | Recommendation | Rationale
|-----|-----
| API style | **Django REST Framework** (not GraphQL) | Simpler, better tooling, sufficient for this domain. GraphQL adds complexity without proportional benefit for a CRUD+editor app
| Resume editor | **TipTap** (ProseMirror) for rich text, **Vue.Draggable** (SortableJS) for section reordering | Battle-tested, Vue-native, great DX
| PDF generation | **WeasyPrint** (primary) + Playwright fallback | WeasyPrint is Python-native, handles CSS well, no browser dependency. Playwright fallback for complex templates
| Auth | **JWT** (access + refresh tokens) via `djangorestframework-simplejwt` | Stateless, works well with SPA. HttpOnly cookie for refresh token
| File storage | **django-storages** → S3-compatible (Hetzner Object Storage or AWS S3 eu-central-1) | EU data residency, cost-effective
| Task queue | **Celery + Redis** | PDF generation, email sending, GDPR data exports, scheduled cleanups
| Search | **PostgreSQL full-text search** initially → **Meilisearch** when needed | Keep stack simple, upgrade when template/job search demands grow
| Caching | **Redis** | Session cache, rate limiting, editor autosave buffer
| Deployment | **Hetzner Cloud** (Nuremberg/Falkenstein) or **AWS eu-central-1** (Frankfurt) | German data residency, DSGVO compliance


### PostgreSQL Schema Outline (Key Tables)

Beyond the schemas listed in sections 1 and 2, additional tables:

```sql
-- Audit log for GDPR accountability
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50), -- 'login', 'export_pdf', 'delete_resume', etc.
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Template versions (for A/B testing and rollback)
CREATE TABLE template_versions (
    id SERIAL PRIMARY KEY,
    template_id INT REFERENCES templates(id),
    version INT,
    css TEXT,
    layout_config JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zeugnisse / document uploads
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(50), -- 'zeugnis', 'zertifikat', 'arbeitszeugnis', 'sonstiges'
    storage_key VARCHAR(500),
    file_size_bytes BIGINT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- B2B: organization invitations
CREATE TABLE org_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    email VARCHAR(255),
    role VARCHAR(50),
    token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Deployment Architecture

```plaintext
                    ┌─────────────┐
                    │  Cloudflare  │
                    │   (CDN/WAF)  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Vue.js Static   │    │  Django API       │
    │  (Hetzner/Vercel)│    │  (Hetzner Cloud)  │
    └──────────────────┘    │  Gunicorn + Nginx │
                            └────────┬─────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
             ┌───────────┐  ┌──────────────┐  ┌───────────┐
             │ PostgreSQL │  │    Redis      │  │ S3 Storage│
             │ (Managed)  │  │  (Managed)    │  │ (Hetzner) │
             └───────────┘  └──────────────┘  └───────────┘
```

---

## 4. Dashboard Specifications

### User Dashboard (B2C)

```plaintext
┌─────────────────────────────────────────────────────┐
│  Logo    Meine Bewerbungen    Vorlagen    Konto  [?]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─ Subscription Banner ──────────────────────────┐ │
│  │ Free Plan · 1/1 Lebenslauf │ [Upgrade →]       │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  [+ Neuen Lebenslauf erstellen]                     │
│                                                     │
│  ┌─ Resume Card ──────────┐ ┌─ Resume Card ──────┐ │
│  │ 📄 "Bewerbung SAP"     │ │ 📄 "IT Freelance"  │ │
│  │ Vorlage: Modern Blau   │ │ Vorlage: Klassisch │ │
│  │ Geändert: 03.03.2026   │ │ Geändert: 01.03.26 │ │
│  │ [Bearbeiten] [⬇ PDF]   │ │ [Bearbeiten] [⬇]  │ │
│  │ [Duplizieren] [🗑]     │ │ [Duplizieren] [🗑] │ │
│  └────────────────────────┘ └────────────────────┘ │
│                                                     │
│  ── Meine Dokumente ──                              │
│  Arbeitszeugnisse (3) │ Zertifikate (2) │ [Upload]  │
│                                                     │
│  ── Datenschutz ──                                  │
│  [Meine Daten herunterladen]  [Konto löschen]       │
└─────────────────────────────────────────────────────┘
```

**Creation flow:**

1. Click "Neuen Lebenslauf erstellen"
2. Choose: Start fresh / Import from LinkedIn / Upload existing PDF
3. Select template (gallery with live previews, premium badges)
4. Select language (Deutsch / English)
5. → Redirect to `/editor/:id`


### Admin Dashboard

```plaintext
Sections:
├── Übersicht (Overview)
│   ├── MRR, ARR, active subscriptions
│   ├── New signups (today/week/month)
│   ├── Churn rate, conversion rate (free → paid)
│   └── Revenue chart (Stripe-synced)
├── Benutzer (Users)
│   ├── Searchable/filterable user table
│   ├── Per-user: plan, resumes count, last active, actions
│   └── Impersonate user (for support)
├── DSGVO-Anfragen (GDPR Requests)
│   ├── Queue of pending data access/deletion requests
│   ├── Status tracking, one-click fulfill
│   └── Audit trail per request
├── Vorlagen (Templates)
│   ├── Template CRUD with live preview
│   ├── Category management
│   └── Premium/free toggle, sort order
├── Abrechnung (Billing)
│   ├── Invoice history (synced from Stripe)
│   ├── Failed payment retry queue
│   └── Refund management
└── System
    ├── Audit log viewer
    ├── Email template editor
    └── Feature flags
```

### B2B/HR Dashboard

```plaintext
Sections:
├── Pipeline (Kanban)
│   ├── Columns: Neu │ In Prüfung │ Vorauswahl │ Abgelehnt │ Eingestellt
│   ├── Drag candidates between stages
│   ├── Quick actions: Star, Note, Email
│   └── Filter by role, department, date
├── Kandidaten (Candidates)
│   ├── Table view: Name, Position, Status, Added, Source
│   ├── Bulk actions: Export list, Send to hiring manager
│   ├── Click → Candidate detail with formatted resume preview
│   └── Side-by-side candidate comparison
├── Vorlagen (Agency templates)
│   ├── Company-branded resume templates
│   ├── Upload candidate data → auto-format into template
│   └── White-label PDF export (agency branding, not platform)
├── Team
│   ├── Member management, role assignment
│   ├── Activity feed: who reviewed/moved whom
│   └── Seat management tied to subscription
└── Berichte (Reports)
    ├── Time-to-fill by role
    ├── Source effectiveness
    ├── Team activity metrics
    └── Export to CSV/Excel
```

---

## 5. Open Architecture Questions & Tradeoff Analysis

### 1. Monolith vs. Microservices

|  | Django Monolith | Microservices
|-----|-----
| **Recommendation** | **Start here** | Migrate later
| Rationale | Faster to build, easier to debug, one deployment. Django's app system provides modular boundaries internally | Premature for < 50k users. PDF generation can be extracted first as an independent service when load demands it


**Decision: Modular monolith.** Use Django apps as boundaries (`apps/accounts`, `apps/resumes`, `apps/billing`, `apps/b2b`, `apps/gdpr`). Extract PDF service first when scaling.

### 2. Template Rendering Strategy

| Option | Approach | Tradeoff
|-----|-----
| **A: HTML/CSS templates** | Templates are HTML+CSS, rendered server-side for PDF | Full CSS control, but CSS-to-PDF fidelity issues
| **B: Vue component templates** | Templates are Vue components, rendered in-browser, Playwright captures PDF | Perfect WYSIWYG, but heavier infrastructure
| **C: Hybrid** | Vue for editor preview, WeasyPrint-compatible HTML/CSS for PDF | Best of both worlds, but maintain two rendering paths


**Recommendation: Option C (Hybrid).** Accept the dual maintenance cost because WYSIWYG accuracy and server-side PDF speed are both critical. Share a common CSS design token system between both renderers to minimize drift.

### 3. B2B Access Model

| Option | Description | Tradeoff
|-----|-----
| **Separate apps** | B2C and B2B are different deployments | Full isolation but double maintenance
| **Feature flags** | Same app, B2B features unlocked by org membership | Simpler, but risk of B2B complexity leaking into B2C
| **Shared core + B2B module** | Core resume engine shared, B2B is a Django app with its own routes/views | Clean separation, shared resume logic


**Recommendation: Shared core + B2B module.** The resume editor and template engine are the same for both. B2B adds pipeline, team management, and white-label on top.

### 4. Multi-Tenancy Approach

| Option | Description | When to use
|-----|-----
| **Shared schema, org_id column** | All orgs in same tables, filtered by `org_id` | < 1000 orgs, simpler
| **Schema-per-tenant** | PostgreSQL schemas per org | Stronger isolation, needed for enterprise
| **Database-per-tenant** | Separate DB per org | Maximum isolation, operational overhead


**Recommendation: Shared schema with `org_id`.** Use Row-Level Security in PostgreSQL for isolation. Migrate to schema-per-tenant only if an enterprise client demands it.

### 5. Additional Decisions Needed

| Question | Options | Recommendation
|-----|-----
| **AI Features?** | GPT-powered writing suggestions, auto-fill from LinkedIn | Yes, but as Phase 2. Build the AI suggestion service as a standalone Celery task consumer
| **i18n scope?** | German-only vs. DE+EN vs. full multi-language | Launch DE+EN, with vue-i18n infrastructure ready for more
| **Mobile strategy?** | Responsive web vs. native app | Responsive web only. Resume editing on mobile is poor UX — focus on desktop/tablet
| **Offline support?** | Service workers, local draft storage | Not for MVP. Add editor autosave to Redis, offline is Phase 3
| **Testing strategy?** | Unit + integration + E2E | pytest + factory_boy (Django), Vitest + Cypress (Vue), Playwright for PDF visual regression


---

## Recommended Phased Execution Plan

| Phase | Scope | Duration Estimate
|-----|-----
| **Phase 1: Foundation** | Auth, user accounts, basic resume editor with 3 templates, PDF export (no watermark for MVP), Stripe payments with SEPA, DSGVO basics (consent, Impressum, Datenschutz), deployment on Hetzner | 10-12 weeks
| **Phase 2: Product-Market Fit** | Anschreiben builder, Bewerbungsmappe combined PDF, 10+ templates (industry-specific), premium feature gating, Zeugnisse upload, AI writing suggestions | 6-8 weeks
| **Phase 3: B2B Launch** | Organization accounts, candidate pipeline, white-label exports, team management, B2B pricing/billing | 8-10 weeks
| **Phase 4: Scale** | Extract PDF microservice, advanced analytics, Europass support, ATS integrations API, schema-per-tenant for enterprise | Ongoing


---

This blueprint covers the full architecture from NovoResume's inferred internals through German-specific legal/product requirements to concrete schema designs and deployment topology. The key principle throughout: **start as a modular Django monolith, build for the German market first-class (not as a localization afterthought), and layer B2B on a shared core.** Each section above can be handed directly to the relevant engineering team as a specification starting point.