---
name: lebenslauf-templates
description: >
  This skill should be used when the user asks to "create a CV template", "design a Lebenslauf",
  "add a new template category", "implement PDF rendering", "configure WeasyPrint",
  "customize colors or fonts", "build a cover letter template", "create a Deckblatt",
  or mentions template, Vorlage, Lebenslauf design, PDF rendering, WeasyPrint, template catalog,
  print styles, Bewerbungsschreiben template, document design, theme customization,
  or any CV/document template creation task for the German job market.
---

# Lebenslauf Template System

Template system for German Lebenslauf (CV), Bewerbungsschreiben (cover letter), and Deckblatt (cover page) with HTML-to-PDF rendering via WeasyPrint.

## Architecture Note

Templates live server-side in Django. The Vue.js frontend fetches template metadata via API for the catalog/selector. PDF rendering happens entirely server-side (WeasyPrint). HTML preview is also rendered server-side and served to the Vue.js editor's iframe via API endpoint.

## German CV Specifics (vs. International)

- Photo slot (top-right or centered) — standard in Germany
- Persönliche Daten section: Geburtsdatum, Geburtsort, Staatsangehörigkeit, Familienstand
- Chronological order: newest first (anti-chronologisch)
- Unterschrift line at bottom (Ort, Datum)
- Tabellarisch (tabular) format most common
- Professional, conservative design preferred for most industries
- A4 format (210mm x 297mm), not US Letter

## Template Categories

| Category | Style | Target Industry |
|----------|-------|----------------|
| Klassisch | Tabular, formal, conservative | Banking, law, government |
| Modern | Clean sidebar, subtle colors | Tech, startups, marketing |
| Kreativ | Bold design, unique layouts | Design, media, creative |
| Akademisch | Multi-page, publication lists | Research, academia |
| IT/Tech | Skill bars, project showcase | Software, engineering |
| Student | Education-focused, minimal | Entry-level, internships |
| Pflege/Handwerk | Industry-specific sections | Healthcare, trades |

## Rendering Pipeline

```
1. Vue.js Editor: User edits content (JSON in Pinia store)
2. Autosave: PATCH /api/v1/documents/{id}/ → saves JSON to PostgreSQL
3. Preview: GET /api/v1/documents/{id}/preview/
   → Django loads content JSON + template HTML/CSS + theme
   → Renders via Django template engine
   → Returns HTML string for iframe display
4. PDF Export: GET /api/v1/documents/{id}/pdf/
   → Same rendering → WeasyPrint converts to PDF (A4, print CSS)
   → PDF cached in FileField, invalidated on content/style change
   → Returns PDF file for download
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/templates/` | GET | List templates (filterable by category) |
| `/api/v1/templates/{id}/` | GET | Template detail (metadata, thumbnail) |
| `/api/v1/templates/{id}/preview/` | GET | Preview with sample data |
| `/api/v1/themes/` | GET | List available color themes |
| `/api/v1/documents/{id}/preview/` | GET | Render HTML preview |
| `/api/v1/documents/{id}/pdf/` | GET | Generate + download PDF |

## Customization Options

| Feature | Kostenlos | Premium |
|---------|-----------|---------|
| Fonts | 3 | 12 |
| Color themes | 30 | 74 |
| Layout reorder | No | Yes |
| Creative backgrounds | No | Yes |
| Picture styles | Basic | 8 styles |
| Rating styles | Dots | 5 styles |
| Max pages | 2 | 10 |

## Theme System

CSS custom properties injected at render time:

```css
:root {
  --cv-primary: #2563eb;
  --cv-secondary: #64748b;
  --cv-accent: #f59e0b;
  --cv-text: #1e293b;
  --cv-background: #ffffff;
  --cv-font-heading: 'Inter', sans-serif;
  --cv-font-body: 'Source Sans Pro', sans-serif;
}
```

All fonts are self-hosted (DSGVO compliance — no Google Fonts CDN).

## Additional Resources

### Reference Files

For detailed template HTML/CSS patterns and rendering engine:
- **`references/template-designs.md`** — HTML structures, CSS patterns, section-specific designs
- **`references/rendering-engine.md`** — WeasyPrint config, Django models, print CSS, caching
