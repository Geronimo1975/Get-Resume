---
name: vue-dashboard
description: >
  This skill should be used when the user asks to "build the dashboard", "create Mein Bereich",
  "implement document management", "build user settings page", "create admin panel",
  "add subscription management UI", "implement DSGVO user controls",
  "build the Bewerbungsmappe interface", or mentions dashboard, Mein Bereich, Konto,
  document list, user settings, admin panel, analytics, revenue metrics, GDPR management,
  Bewerbungsmappe, user interface, document management, subscription management,
  team management, B2B dashboard, or any authenticated user interface.
  Triggers on: dashboard, Mein Bereich, Konto, admin, analytics, document grid,
  subscription UI, DSGVO settings, team members, Abo, Zahlung, Datenschutz settings.
---

# Vue.js Dashboard Components

Vue.js 3 SPA dashboard for the GetResume platform — user dashboard (Mein Bereich), admin panel, and B2B light team management.

## Architecture

- **Vue.js 3** with Composition API + TypeScript
- **Pinia** stores for dashboard state
- **Vue Router** nested routes under `/dashboard`
- **Tailwind CSS** + Headless UI for styling
- **Chart.js** + vue-chartjs for admin analytics
- **Axios** for API communication with Django DRF backend

## Route Structure

```
/dashboard                    → DashboardView.vue (layout wrapper)
├── /dashboard/dokumente      → MeineDokumente.vue (default)
├── /dashboard/jobs           → JobsView.vue
├── /dashboard/bewerbungen    → BewerbungenView.vue (pipeline)
├── /dashboard/mappe          → BewerbungsmappeView.vue
├── /dashboard/konto          → KontoView.vue
├── /dashboard/abo            → AboZahlungView.vue
├── /dashboard/datenschutz    → DatenschutzView.vue
├── /dashboard/team           → TeamView.vue (B2B light)
└── /dashboard/hilfe          → HilfeView.vue
```

## Component Structure

```
src/components/dashboard/
├── DashboardLayout.vue        # Sidebar + content area
├── DashboardSidebar.vue       # Navigation links
├── documents/
│   ├── DocumentGrid.vue       # Grid/list toggle view
│   ├── DocumentCard.vue       # Single document card
│   ├── DocumentActions.vue    # Edit, duplicate, download, delete
│   └── EmptyState.vue         # "Erstellen Sie Ihren ersten Lebenslauf"
├── jobs/
│   ├── ScrapingConfig.vue     # Platform + keyword setup
│   ├── JobResultsTable.vue    # Filterable job list
│   └── JobActions.vue         # Apply, generate CL, dismiss
├── pipeline/
│   ├── KanbanBoard.vue        # Draggable columns
│   ├── ApplicationCard.vue    # Single application
│   └── PipelineStats.vue      # Analytics charts
├── settings/
│   ├── ProfileForm.vue        # Name, email, password
│   ├── SubscriptionCard.vue   # Current plan + actions
│   ├── PaymentHistory.vue     # Invoice list + download
│   ├── WiderrufButton.vue     # 14-day withdrawal
│   └── DatenschutzControls.vue # GDPR: export, delete, consent
├── team/
│   ├── TeamMembers.vue        # Member list + roles
│   ├── InviteMember.vue       # Invite by email
│   └── TeamSettings.vue       # Team name, plan
└── admin/
    ├── AdminDashboard.vue     # Revenue + user metrics
    ├── UserManagement.vue     # User table with filters
    ├── GDPRPanel.vue          # DSGVO requests management
    └── ContentManager.vue     # Templates + blog posts
```

## User Dashboard (Mein Bereich)

### Sidebar Navigation

- Meine Dokumente (default active)
- Stellenangebote (Jobs)
- Bewerbungen (Pipeline)
- Bewerbungsmappe
- Konto-Einstellungen
- Abo & Zahlung
- Datenschutz
- Team (B2B only)
- Hilfe & Support

### Meine Dokumente

- Grid view (default) / List view toggle
- Document cards: thumbnail + title + type badge + last edited + actions
- Actions: Bearbeiten, Duplizieren, Herunterladen (PDF), Löschen
- Premium lock overlay for free users on premium features
- Filter by doc_type: Lebenslauf | Anschreiben | Deckblatt
- Sort by: Zuletzt bearbeitet | Name | Erstellt am
- Infinite scroll with intersection observer
- Empty state: illustration + "Erstellen Sie Ihren ersten Lebenslauf" CTA

### Abo & Zahlung

- Current plan card with status badge (Aktiv / Gekündigt / Abgelaufen)
- Payment history table with invoice PDF download links
- Upgrade / Downgrade → Stripe Checkout via API
- Cancel subscription with confirmation dialog
- Widerruf button (visible within 14-day window)
- Invoice (Rechnung) download list

### Datenschutz Settings

- Cookie consent management (update preferences via API)
- Data export request button (Art. 20 DSGVO)
- Account deletion request (Art. 17 DSGVO) with confirmation
- Consent log viewer
- Marketing/Newsletter toggles

## Admin Dashboard

- Revenue charts: MRR, ARR, conversion rate, churn rate (Chart.js)
- User stats: total, active, premium, new this month
- Document stats: created today/week/month, popular templates
- DSGVO Panel: pending deletion requests, pending export requests, audit log

## B2B Light — Team Dashboard

- Team member list with roles (Admin / Member)
- Invite member by email
- Remove member with confirmation
- Shared template library
- Usage analytics per team member

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/documents/` | GET | List documents |
| `/api/v1/documents/{id}/` | DELETE | Soft delete |
| `/api/v1/documents/{id}/duplicate/` | POST | Clone |
| `/api/v1/documents/{id}/pdf/` | GET | Download PDF |
| `/api/v1/users/me/` | GET/PATCH | Profile |
| `/api/v1/users/me/gdpr/export/` | POST | Data export |
| `/api/v1/users/me/gdpr/delete/` | POST | Delete account |
| `/api/v1/payments/subscription/` | GET | Current plan |
| `/api/v1/payments/invoices/` | GET | Invoice list |
| `/api/v1/teams/{id}/members/` | GET | Team members |
| `/api/v1/teams/{id}/invite/` | POST | Invite member |

## Additional Resources

### Reference Files

For detailed view implementations and component patterns:
- **`references/dashboard-views.md`** — Django DRF views for dashboard API endpoints
- **`references/dashboard-templates.md`** — Vue component patterns and interactions
