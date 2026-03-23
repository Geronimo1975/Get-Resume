---
name: german-legal-compliance
description: >
  This skill should be used when the user asks to "create an Impressum", "implement cookie consent",
  "add DSGVO compliance", "create privacy policy", "build AGB page", "implement Widerrufsbelehrung",
  "generate GoBD invoice", "handle GDPR requests", "add cookie banner", "implement data deletion",
  or mentions DSGVO, GDPR, BDSG, TTDSG, Datenschutz, Impressum, cookie consent, AGB, privacy policy,
  Widerrufsrecht, Rechnung, MwSt, audit log, data export, data portability, or any compliance-related
  implementation for the German market. CRITICAL: Always consult this skill before creating any legal
  page or data handling feature — German law imposes severe penalties (up to 4% annual turnover or
  20M EUR for DSGVO violations, up to 50,000 EUR for missing Impressum).
---

# German Legal Compliance Framework

Complete legal compliance framework for SaaS platforms operating in Germany. Covers DSGVO (GDPR), BDSG, TTDSG, TMG/DDG, BGB, PAngV, GoBD, and AO requirements.

## Architecture Note

This platform uses a **Vue.js SPA + Django REST API** architecture. Legal pages (Impressum, Datenschutz, AGB) are rendered by the Vue.js frontend using data from API endpoints. Cookie consent is managed client-side in the Vue.js app with server-side persistence via API.

## Legal Documents Required (Minimum Viable Legal)

### 1. Impressum (MANDATORY — TMG §5 / DDG Art. 5)

- Accessible within 2 clicks from ANY page
- Link labeled "Impressum" in footer on EVERY page (Vue Router link)
- Fine up to 50,000 EUR for missing/incomplete Impressum
- Separate page from Datenschutzerklaerung

**Required fields:** Full company name + legal form, physical address (no PO box), email + second contact method, Handelsregister number + Amtsgericht, USt-IdNr., Steuernummer, Geschaeftsfuehrer name.

### 2. Datenschutzerklaerung (MANDATORY — Art. 13/14 DSGVO)

- In German language, accessible from every page
- List EVERY data processing activity with: Zweck, Rechtsgrundlage (Art. 6 DSGVO), Empfaenger, Speicherdauer, Drittlandtransfer mechanism
- All cookies listed individually: Name, Provider, Purpose, Duration, Type
- Betroffenenrechte section (Art. 15-22 DSGVO)
- Beschwerderecht to supervisory authority

### 3. Cookie Consent Banner (MANDATORY — TTDSG §25)

**Implementation in Vue.js SPA:**

The cookie consent banner is a Vue.js component (`CookieConsentBanner.vue`) that:
- Renders as overlay on first visit (before any tracking loads)
- Stores consent in Pinia store + localStorage + API persistence
- Blocks all non-essential scripts until consent given

**Layer 1 (Initial Banner):**
- 3 equal buttons: "Alle akzeptieren" | "Einstellungen" | "Nur notwendige"
- NO pre-checked non-essential cookies
- NO "X" close button without choice
- Block ALL tracking scripts before consent

**Layer 2 (Settings):**
- Individual toggles per category: Notwendig (always ON, disabled), Statistik (OFF default), Marketing (OFF default), Externe Medien (OFF default)
- Cookie list under each category

**Layer 3 (Details):**
- Full cookie table: Name | Anbieter | Zweck | Ablauf | Typ

### 4. AGB (MANDATORY — §312d BGB)

- Same language as website
- Prices MUST include MwSt (PAngV)
- ODR link mandatory: `https://ec.europa.eu/consumers/odr`

### 5. Widerrufsbelehrung (MANDATORY — §312g BGB)

- 14 calendar days withdrawal right
- Model withdrawal form available for download
- Show BEFORE payment completion
- Checkbox confirmation required at checkout

### 6. Rechnungen (GoBD compliant)

- Sequential invoice numbers (no gaps), format: RE-YYYY-NNNNN
- Net + MwSt (19%) + Gross breakdown
- 10-year retention (Aufbewahrungspflicht AO §147)

## Cookie Consent — Vue.js Implementation

```typescript
// stores/consent.ts (Pinia)
interface ConsentState {
  hasConsented: boolean
  necessary: true        // always true
  statistics: boolean    // default false
  marketing: boolean     // default false
  externalMedia: boolean // default false
  consentVersion: string
  consentTimestamp: string | null
}

// On consent change:
// 1. Update Pinia store
// 2. Save to localStorage
// 3. POST /api/v1/legal/cookie-consent/ (persist server-side)
// 4. Conditionally load/unload tracking scripts
```

- Google Fonts MUST be self-hosted (Landgericht München ruling)
- YouTube embeds: thumbnail + click-to-load with consent check
- Google Analytics / Plausible: only load after Statistik consent
- Consent log stored server-side: UUID, timestamp, IP (hashed), choices

## DSGVO User Rights — API Endpoints

| Right | Article | API Endpoint | Method |
|-------|---------|-------------|--------|
| Auskunftsrecht | Art. 15 | `/api/v1/users/me/gdpr/export/` | POST |
| Recht auf Löschung | Art. 17 | `/api/v1/users/me/gdpr/delete/` | POST |
| Datenportabilität | Art. 20 | `/api/v1/users/me/gdpr/export/` | POST |
| Berichtigung | Art. 16 | `/api/v1/users/me/` | PATCH |
| Cookie Consent | TTDSG §25 | `/api/v1/legal/cookie-consent/` | GET/POST |

All requests logged in AuditLog. Automated confirmation emails for all GDPR requests.

## Implementation Priority

1. Impressum page (Vue route + API data)
2. Datenschutzerklaerung (Vue route + API data)
3. Cookie consent banner (Vue component + Pinia store + API)
4. AGB page (Vue route)
5. Widerrufsbelehrung (shown at checkout)
6. GDPR user rights API endpoints
7. GoBD-compliant invoice generation
8. Automated GDPR cleanup Celery task
9. Consent audit report

## Additional Resources

### Reference Files

For complete legal page templates, model schemas, and implementation details:
- **`references/legal-pages.md`** — Legal page content, Vue component patterns
- **`references/gdpr-implementation.md`** — GDPR models, API views, Celery tasks, invoice generation
