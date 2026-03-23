You are a senior full-stack engineer specializing in modern SaaS frontend architecture. Your task is to build a complete, production-ready frontend for a German-market SaaS resume/CV builder platform (Lebenslauf-Builder) based on the technical blueprint provided.

## Core Requirements

**Tech Stack:**
- Framework: React with Next.js (App Router)
- Styling: Tailwind CSS with shadcn/ui component library
- Language: TypeScript with fully typed interfaces derived from the schema
- Structure: Multi-tenant aware, role-based access control (RBAC), authentication flows (login, signup, password reset, OAuth), and a dashboard shell layout

**Schema Implementation:**
Analyze **Blueprint_Lebenslauf_SaaS_Germania.docx** thoroughly. Map every entity and relationship to the appropriate UI components, forms, tables, and views. The schema includes:
- User/UserProfile models with GDPR consent tracking and deletion request fields
- Document models storing CV content as JSON (personal_data, berufserfahrung, ausbildung, sprachen, etc.)
- Subscription/Payment/Invoice models with VAT tracking and sequential invoice numbering per German law
- Template models with category taxonomy (modern, klassisch, kreativ, akademisch, IT)

All data models must be reflected accurately—form validations, field types, and entity relationships must match the schema exactly.

## German-Specific SaaS Features

Implement native support for:
- **Lebenslauf** (CV/resume) with photo slot and Lebenslauf-specific formatting
- **Bewerbungsschreiben** (cover letter) editor
- **Deckblatt** (cover page) builder
- **Bewerbungsmappe** (complete application folder) combining all documents
- Industry-specific templates: Handwerk, IT, Pflege, Ingenieurwesen
- Bilingual DE/EN interface with German as primary language
- PDF generation for all document types

## Legal Compliance (Non-Negotiable)

Implement:
- **DSGVO/GDPR:** Granular cookie consent per TTDSG with separate toggles (Notwendig, Statistik, Marketing, Externe Medien)
- **Legal Pages:** Mandatory Impressum (TMG §5), complete Datenschutzerklärung, AGB with Widerrufsbelehrung (14-day withdrawal right)
- **Pricing Display:** All prices shown gross including 19% MwSt per PAngV
- **Billing:** GoBD-compliant invoice handling with sequential numbering and 10-year retention logic

## Pricing Tiers UI

Build subscription management pages reflecting:
- **Free Tier:** 1 page, 1 version, 3 fonts
- **Premium Monthly:** €17.99
- **Premium Quarterly:** €34.99
- **Premium Annual:** €109.99
- Non-subscription payment option support

## SaaS UI/UX Architecture

Implement a responsive, accessible dashboard with:
- Sidebar navigation with document/template organization
- Topbar with user menu, notifications, billing status
- Content areas for:
  - **Dashboard / Overview:** Document list, recent activity, quick-start templates
  - **CV/Document Editor:** Full-featured editor for Lebenslauf, Bewerbungsschreiben, Deckblatt
  - **Template Management:** Browse, filter by category/industry, apply templates
  - **User Management:** Profile, preferences, connected accounts
  - **Subscription & Billing:** Current plan, usage, invoices, payment methods
  - **Settings:** DSGVO consent management, data deletion, language, privacy preferences

## Code Quality Standards

- Clean, modular, production-grade code with clear separation of concerns: `components/`, `hooks/`, `services/`, `types/`, `lib/`
- Error handling, loading states, and empty states on all data-fetching components
- Reusable components following consistent naming conventions
- Accessibility (WCAG 2.1 AA compliant)
- No placeholders, no TODOs, no incomplete implementations
- Production-ready error boundaries and form validation

## Deliverable

Provide the complete file and folder structure, then output full, working code for every file. Prioritize core entities first: User authentication → Document models → Editor interface → Template system → Subscription/billing → Legal compliance pages. Build systematically outward.

**Schema provided in Blueprint_Lebenslauf_SaaS_Germania.docx — analyze it fully before generating any code.**