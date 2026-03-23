---
name: karriere-blog-seo
description: >
  This skill should be used when the user asks to "create the blog", "add SEO",
  "implement structured data", "generate XML sitemap", "configure meta tags",
  "write a blog article template", "add Open Graph tags", "set up breadcrumbs",
  "implement hreflang", or mentions blog, Karriere-Blog, SEO, article, sitemap,
  meta tags, structured data, Schema.org, keywords, Open Graph, canonical URLs,
  breadcrumbs, content marketing, search engine optimization, RSS feed,
  or any blog/SEO feature for the German job market.
---

# Karriere-Blog & SEO Engine

SEO-optimized career blog engine for the German job market with structured data, sitemaps, and keyword-targeted content strategy.

## Architecture Note

**SEO Challenge:** Vue.js SPAs are not crawlable by default. For the blog to rank in Google, choose one of:

1. **Pre-rendering (Recommended for MVP):** Use `vite-plugin-ssr` or Prerender.io to generate static HTML for blog pages at build time
2. **Server-side rendering:** Migrate to Nuxt.js for the blog section
3. **Hybrid:** Keep blog as Django-rendered pages (separate from SPA) at `/karriere-blog/`, while the SPA handles dashboard/editor

Option 3 is simplest — Django serves blog HTML directly with full SEO control, while the Vue.js SPA handles authenticated pages.

## Blog API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/blog/` | GET | List published posts (paginated) |
| `/api/v1/blog/{slug}/` | GET | Post detail with structured data |
| `/api/v1/blog/categories/` | GET | List categories |
| `/karriere-blog/sitemap.xml` | GET | XML sitemap (Django view) |
| `/karriere-blog/feed/` | GET | RSS feed (Django view) |

## URL Structure (German-optimized)

```
/karriere-blog/                              → Blog index
/karriere-blog/{slug}/                       → Article
/karriere-blog/kategorie/{slug}/             → Category archive
/karriere-blog/tag/{slug}/                   → Tag archive
/karriere-blog/feed/                         → RSS feed
/karriere-blog/sitemap.xml                   → Blog sitemap
```

## SEO Features

- django-meta for per-page meta tag management
- Auto-generated meta description from excerpt (max 155 chars)
- Canonical URLs on all pages
- hreflang tags for DE/EN versions
- XML sitemap with lastmod, changefreq, priority
- robots.txt with sitemap reference
- Breadcrumb navigation (BreadcrumbList schema)

## Structured Data (JSON-LD)

| Schema Type | Pages | Purpose |
|-------------|-------|---------|
| Organization | All (base template) | Brand identity, social links |
| Product + Offer | Pricing page | SaaS product with EUR pricing |
| FAQPage | FAQ sections, pillar articles | FAQ rich snippets |
| BlogPosting | Article detail pages | Article rich snippets |
| HowTo | Tutorial articles | Step-by-step rich snippets |
| BreadcrumbList | All blog pages | Breadcrumb rich snippets |
| AggregateRating | Template pages, homepage | Star ratings in SERPs |

## Target Keywords (Primary)

| Keyword | Monthly Volume | Content Type |
|---------|---------------|-------------|
| Lebenslauf Vorlage | 90,500 | Pillar article + templates |
| Lebenslauf erstellen | 49,500 | Pillar article + editor CTA |
| Bewerbungsschreiben Muster | 33,100 | Pillar article + templates |
| tabellarischer Lebenslauf | 27,100 | Cluster article |
| CV erstellen kostenlos | 22,200 | Landing page + blog CTA |

## Content Strategy

- 1 pillar article per main keyword (2000+ words)
- 5-10 cluster articles linking back to pillar
- Internal linking: blog ↔ templates ↔ editor
- CTA widgets in sidebar and inline (template preview + "Jetzt erstellen")
- Author byline with expertise for E-E-A-T signals

## Additional Resources

### Reference Files

For detailed model definitions, views, and structured data:
- **`references/blog-models-views.md`** — Article, Category, Tag models, DRF views, RSS, sitemap
- **`references/seo-structured-data.md`** — JSON-LD templates, meta tags, robots.txt, hreflang
