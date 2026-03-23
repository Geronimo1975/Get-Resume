---
name: stripe-payment-de
description: >
  This skill should be used when the user asks to "implement payments", "set up Stripe",
  "create checkout flow", "add subscription management", "generate invoices",
  "implement Widerrufsrecht", "handle webhooks", "create pricing page",
  or mentions payment, Stripe, checkout, subscription, pricing, MwSt, Rechnung, invoice,
  SEPA, Giropay, Widerrufsrecht, refund, billing, Preise, Abo, financial transaction,
  or any payment-related feature for the German market.
---

# Stripe Payment Integration (German Market)

Complete Stripe payment integration optimized for Germany with SEPA, MwSt handling, GoBD-compliant invoicing, and 14-day Widerrufsrecht. API-driven for Vue.js SPA frontend.

## Plugin Settings

Check `.claude/lebenslauf-builder-skills.local.md` for project-specific config:

- `stripe_configured` — whether Stripe keys are set (skip payment features if `false`)
- `stripe_mode` — `"test"` or `"live"` (controls which key prefix to expect)
- `mwst_rate` — MwSt percentage (default: `19`)

## Architecture Note

Payments use **Stripe Checkout Sessions** created via Django DRF API endpoints. The Vue.js frontend redirects to Stripe's hosted checkout page (PCI compliance). Webhook events are processed server-side by Django.

## Payment Methods (Priority for DE)

1. Kreditkarte (Visa/Mastercard) — via Stripe Elements
2. PayPal — via Stripe PayPal integration
3. SEPA-Lastschrift — via Stripe SEPA Direct Debit
4. Sofort/Klarna — via Stripe Sofort
5. Giropay — via Stripe Giropay
6. Apple Pay / Google Pay — via Stripe Payment Request Button

## Pricing Rules (PAngV — Preisangabenverordnung)

- ALL prices shown to consumers MUST include MwSt (19%)
- Display format: `9,99 € inkl. MwSt` (German comma decimal)
- Net price + MwSt breakdown shown at checkout
- Currency: EUR only

## Subscription Plans

| Plan | Price (brutto) | Billing | Key Features |
|------|---------------|---------|-------------|
| Kostenlos | 0 € | — | 1 CV, 3 templates, watermark |
| Premium | 9,99 €/mo | Monthly | Unlimited, all templates, 50 jobs, 10 cover letters |
| Premium Yearly | 7,99 €/mo | Yearly (95,88 €) | Same as Premium + 2 months free |
| Business | 24,99 €/mo | Monthly | Team (5 members), 500 jobs, 100 cover letters |

## Checkout Flow (SPA)

1. User selects plan on `/preise` (Vue PricingView)
2. Vue.js shows legal checkboxes BEFORE proceeding (all required):
   - `[ ]` Ich habe die AGB gelesen und akzeptiere diese
   - `[ ]` Ich habe die Widerrufsbelehrung zur Kenntnis genommen
   - `[ ]` Ich stimme zu, dass die Dienstleistung sofort beginnt
3. POST `/api/v1/payments/checkout/` → creates Stripe Checkout Session
4. Frontend redirects to `session.url` (Stripe hosted checkout)
5. Stripe webhook: `checkout.session.completed` → activate subscription
6. Redirect to `/dashboard/abo?success=true` + send confirmation email + invoice PDF

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/payments/plans/` | GET | List subscription plans with EUR prices |
| `/api/v1/payments/checkout/` | POST | Create Stripe Checkout Session |
| `/api/v1/payments/subscription/` | GET | Current subscription details |
| `/api/v1/payments/subscription/cancel/` | POST | Cancel at period end |
| `/api/v1/payments/subscription/widerruf/` | POST | 14-day withdrawal + refund |
| `/api/v1/payments/invoices/` | GET | List all invoices |
| `/api/v1/payments/invoices/{id}/pdf/` | GET | Download invoice PDF |
| `/api/v1/webhooks/stripe/` | POST | Stripe webhook handler |

## Widerrufsrecht (14-day Withdrawal)

- Timer starts at payment completion
- Dashboard shows "Widerruf einreichen" button during 14-day window
- Pro-rata calculation if sofort-Beginn was accepted
- Automated refund via Stripe Refund API
- Email confirmation (Widerrufsbestätigung)
- Generate Stornorechnung (credit note)

## Invoice Generation (GoBD)

- Triggered by successful payment webhook
- Sequential Rechnungsnummer (format: RE-2026-00001, no gaps)
- PDF via WeasyPrint with company letterhead
- Fields: Rechnungsnummer, Rechnungsdatum, Leistungszeitraum, Nettobetrag, MwSt-Satz (19%), MwSt-Betrag, Bruttobetrag
- Stored 10 years (Aufbewahrungspflicht AO §147)
- Available for download in user dashboard via API

## Webhook Events Handled

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Activate subscription, create invoice |
| `payment_intent.succeeded` | Log payment |
| `customer.subscription.updated` | Sync plan changes |
| `customer.subscription.deleted` | Downgrade to Free |
| `invoice.paid` | Generate GoBD invoice PDF |
| `invoice.payment_failed` | Dunning email, 7-day grace |

## Additional Resources

### Reference Files

For detailed view implementations and invoice system:
- **`references/stripe-views.md`** — DRF views for checkout, webhook, subscription management
- **`references/invoice-system.md`** — GoBD invoice model, PDF generation, retention policy
