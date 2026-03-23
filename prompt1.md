You are a senior full-stack software architect and product strategist with deep expertise in SaaS platforms, resume/CV builders, German labor market regulations, GDPR/DSGVO compliance, and payment system integration.

I am at the very beginning of planning a platform that clones NovoResume (https://novoresume.com/) and fully adapts it for the **German job market (Arbeitsmarkt)**. The platform serves four user groups: **job seekers in Germany (B2C)**, **companies and HR teams recruiting in Germany (B2B)**, **recruitment agencies as intermediaries**, and potentially both B2C and B2B simultaneously. The tech stack is **Vue.js + Django + PostgreSQL**. I need a complete architectural exploration and structured execution plan I can hand to a development team.

Act as my thinking partner and produce a comprehensive technical and product blueprint across these dimensions:

## Platform Analysis

Analyze NovoResume exhaustively—infer its full frontend architecture (routing, UI components, resume editor with drag-and-drop and real-time preview, template system, user flows), backend architecture (database schema for users, resumes, templates, subscriptions, payments, sessions), API structure, authentication, PDF generation pipeline, file storage strategy, and subscription/payment logic including free vs. premium feature gating.

## German Market Adaptation

Design the full adaptation for the German market:

- **CV/Lebenslauf specifics**: German CV format standards (Lichtbild/photo section, Anschreiben integration, Lebenslauf vs. Europass formats, Zeugnisse upload), industry-specific templates for German sectors (IT, Ingenieurwesen, Gesundheitswesen, Verwaltung)
- **B2B layer**: how the platform serves HR teams and recruitment agencies—multi-user accounts, candidate pipeline views, bulk resume review, or white-label considerations
- **Legal and compliance architecture**:
  - Full **GDPR/DSGVO compliance**: data minimization, right to erasure, data portability, consent management
  - **Cookie consent popup** (IAB TCF 2.x compliant, opt-in by default for non-essential cookies, granular consent categories)
  - **Impressum** auto-generation logic
  - **Datenschutzerklärung** template compliant with DSGVO
  - Data processing agreements (AVV/DPA)
  - EU/German server data residency requirements
- **Payment system**: Stripe or Mollie integration with SEPA Direct Debit, German invoicing requirements (VAT/MwSt., Kleinunternehmerregelung), recurring billing, cancellation policy compliant with Fernabsatzgesetz

## Technical Stack Blueprint (Vue.js + Django + PostgreSQL)

Provide a complete stack recommendation built around Vue.js (frontend), Django (backend), and PostgreSQL (database), covering: resume editor library, PDF generation approach, Django REST vs. GraphQL decision, ORM and PostgreSQL schema outline, auth strategy, file storage, CDN, payment provider and webhook architecture, and EU-region compliant deployment infrastructure.

## Dashboard Specifications

Specify both dashboards in detail:

- **User Dashboard**: resume list, creation flow, template picker, download manager, subscription status, GDPR data controls (download my data, delete my account)
- **Admin Dashboard**: user table, subscription analytics, MRR/churn metrics, GDPR request queue, template management
- **B2B/HR Dashboard**: what this needs to look like for recruiters and agencies managing candidates

## Open Architecture Questions

Identify the key decisions I still need to make before development begins—such as monolith vs. microservices, template rendering strategy, B2B access model, multi-tenancy approach—and help me think through the tradeoffs for each in this specific context.