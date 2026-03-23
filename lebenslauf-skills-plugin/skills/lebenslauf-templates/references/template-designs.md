# Template Designs Reference

Detailed CV template design patterns for German Lebenslauf, Bewerbungsschreiben, and Deckblatt.

---

## 1. Base Template HTML Structure

All CV templates inherit from this base structure.

```html
{# templates/cv/base_cv.html #}

<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ document.title }}</title>

  {# Self-hosted fonts — LG München ruling requires no Google Fonts CDN #}
  <style>
    {% include "cv/fonts.css" %}
  </style>

  {# Theme CSS custom properties #}
  <style>
    :root {
      {% block theme_variables %}
      --cv-primary: {{ theme.primary|default:"#2563eb" }};
      --cv-secondary: {{ theme.secondary|default:"#64748b" }};
      --cv-accent: {{ theme.accent|default:"#f59e0b" }};
      --cv-text: {{ theme.text|default:"#1e293b" }};
      --cv-text-light: {{ theme.text_light|default:"#64748b" }};
      --cv-background: {{ theme.background|default:"#ffffff" }};
      --cv-surface: {{ theme.surface|default:"#f8fafc" }};
      --cv-border: {{ theme.border|default:"#e2e8f0" }};
      --cv-font-heading: {{ theme.font_heading|default:"'Inter', sans-serif" }};
      --cv-font-body: {{ theme.font_body|default:"'Source Sans Pro', sans-serif" }};
      --cv-font-size-base: {{ theme.font_size_base|default:"10pt" }};
      --cv-line-height: {{ theme.line_height|default:"1.5" }};
      {% endblock %}
    }
  </style>

  {# Template-specific CSS #}
  <style>
    {% block template_css %}{% endblock %}
  </style>

  {# Print CSS for PDF rendering #}
  <style media="print">
    {% include "cv/print.css" %}
  </style>
</head>
<body class="cv-body">

  <div class="cv-page" id="cv-page-1">
    {% block page_content %}

      {% block header %}
      {# Personal data: name, photo, contact info #}
      {% endblock %}

      {% block sidebar %}
      {# Optional sidebar for some templates #}
      {% endblock %}

      {% block main %}
      {# Main content area with sections #}
        {% for section in sections %}
          {% if section.is_visible %}
            {% block section_content %}
              {% include "cv/sections/"|add:section.section_type|add:".html" %}
            {% endblock %}
          {% endif %}
        {% endfor %}
      {% endblock %}

      {% block footer %}
      {# Unterschrift section #}
      {% endblock %}

    {% endblock %}
  </div>

</body>
</html>
```

---

## 2. Klassisch Template (Formal / Conservative)

Target: Banking, law, government, traditional German employers.

```html
{# templates/cv/klassisch/lebenslauf.html #}

{% extends "cv/base_cv.html" %}

{% block theme_variables %}
  {{ block.super }}
  --cv-primary: {{ theme.primary|default:"#1e3a5f" }};
  --cv-font-heading: {{ theme.font_heading|default:"'Merriweather', serif" }};
  --cv-font-body: {{ theme.font_body|default:"'Source Sans Pro', sans-serif" }};
{% endblock %}

{% block template_css %}
/* Klassisch Template — Tabular Layout */
.cv-body {
  font-family: var(--cv-font-body);
  font-size: var(--cv-font-size-base);
  line-height: var(--cv-line-height);
  color: var(--cv-text);
  background: var(--cv-background);
}

.cv-page {
  width: 210mm;
  min-height: 297mm;
  padding: 20mm 25mm;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Header: Name left, Photo right */
.cv-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--cv-primary);
}

.cv-header__name {
  font-family: var(--cv-font-heading);
  font-size: 24pt;
  font-weight: 700;
  color: var(--cv-primary);
  margin: 0 0 4px 0;
}

.cv-header__subtitle {
  font-size: 11pt;
  color: var(--cv-text-light);
}

.cv-header__photo {
  width: 35mm;
  height: 45mm;
  object-fit: cover;
  border: 1px solid var(--cv-border);
}

/* Section structure — tabular two-column */
.cv-section {
  margin-bottom: 16px;
}

.cv-section__title {
  font-family: var(--cv-font-heading);
  font-size: 13pt;
  font-weight: 700;
  color: var(--cv-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--cv-border);
  margin-bottom: 10px;
}

/* Tabular entry layout (date | content) */
.cv-entry {
  display: grid;
  grid-template-columns: 85px 1fr;
  gap: 12px;
  margin-bottom: 10px;
}

.cv-entry__date {
  font-size: 9pt;
  color: var(--cv-text-light);
  padding-top: 2px;
}

.cv-entry__title {
  font-weight: 600;
  font-size: 10.5pt;
}

.cv-entry__subtitle {
  font-size: 9.5pt;
  color: var(--cv-text-light);
}

.cv-entry__description {
  font-size: 9.5pt;
  margin-top: 4px;
}

/* Personal data table */
.cv-personal-data {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 4px 12px;
  font-size: 9.5pt;
}

.cv-personal-data__label {
  color: var(--cv-text-light);
}

/* Unterschrift */
.cv-unterschrift {
  margin-top: 24px;
  padding-top: 8px;
}

.cv-unterschrift__line {
  width: 200px;
  border-bottom: 1px solid var(--cv-text);
  margin-top: 40px;
}

.cv-unterschrift__text {
  font-size: 9pt;
  color: var(--cv-text-light);
  margin-top: 4px;
}
{% endblock %}

{% block page_content %}
  {# Header with photo #}
  <header class="cv-header">
    <div>
      <h1 class="cv-header__name">{{ persoenliche_daten.vorname }} {{ persoenliche_daten.nachname }}</h1>
      {% if persoenliche_daten.position %}
        <p class="cv-header__subtitle">{{ persoenliche_daten.position }}</p>
      {% endif %}
    </div>
    {% if persoenliche_daten.foto %}
      <img src="{{ persoenliche_daten.foto }}" alt="Bewerbungsfoto" class="cv-header__photo">
    {% endif %}
  </header>

  {# Personal Data Section #}
  <section class="cv-section">
    <h2 class="cv-section__title">Persönliche Daten</h2>
    <div class="cv-personal-data">
      {% if persoenliche_daten.geburtsdatum %}
        <span class="cv-personal-data__label">Geburtsdatum</span>
        <span>{{ persoenliche_daten.geburtsdatum }}</span>
      {% endif %}
      {% if persoenliche_daten.geburtsort %}
        <span class="cv-personal-data__label">Geburtsort</span>
        <span>{{ persoenliche_daten.geburtsort }}</span>
      {% endif %}
      {% if persoenliche_daten.staatsangehoerigkeit %}
        <span class="cv-personal-data__label">Staatsangehörigkeit</span>
        <span>{{ persoenliche_daten.staatsangehoerigkeit }}</span>
      {% endif %}
      {% if persoenliche_daten.familienstand %}
        <span class="cv-personal-data__label">Familienstand</span>
        <span>{{ persoenliche_daten.familienstand }}</span>
      {% endif %}
      <span class="cv-personal-data__label">E-Mail</span>
      <span>{{ persoenliche_daten.email }}</span>
      {% if persoenliche_daten.telefon %}
        <span class="cv-personal-data__label">Telefon</span>
        <span>{{ persoenliche_daten.telefon }}</span>
      {% endif %}
      <span class="cv-personal-data__label">Anschrift</span>
      <span>{{ persoenliche_daten.strasse }}, {{ persoenliche_daten.plz }} {{ persoenliche_daten.stadt }}</span>
    </div>
  </section>

  {# Rendered sections in order #}
  {% for section in sections %}
    {% if section.is_visible and section.section_type != "persoenliche_daten" and section.section_type != "unterschrift" %}
      {% include "cv/sections/"|add:section.section_type|add:".html" with entries=section.content.eintraege %}
    {% endif %}
  {% endfor %}

  {# Unterschrift #}
  {% if unterschrift %}
    <div class="cv-unterschrift">
      <div class="cv-unterschrift__line"></div>
      <p class="cv-unterschrift__text">{{ unterschrift.ort }}, {{ unterschrift.datum }}</p>
    </div>
  {% endif %}
{% endblock %}
```

---

## 3. Modern Template (Clean Sidebar)

Target: Tech, startups, marketing.

```html
{# templates/cv/modern/lebenslauf.html #}

{% extends "cv/base_cv.html" %}

{% block theme_variables %}
  {{ block.super }}
  --cv-primary: {{ theme.primary|default:"#2563eb" }};
  --cv-sidebar-bg: {{ theme.sidebar_bg|default:"#1e293b" }};
  --cv-sidebar-text: {{ theme.sidebar_text|default:"#f1f5f9" }};
  --cv-font-heading: {{ theme.font_heading|default:"'Inter', sans-serif" }};
  --cv-font-body: {{ theme.font_body|default:"'Inter', sans-serif" }};
{% endblock %}

{% block template_css %}
.cv-page {
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto;
  display: flex;
  overflow: hidden;
}

/* Sidebar (left) */
.cv-sidebar {
  width: 70mm;
  background: var(--cv-sidebar-bg);
  color: var(--cv-sidebar-text);
  padding: 20mm 10mm;
  flex-shrink: 0;
}

.cv-sidebar__photo {
  width: 50mm;
  height: 50mm;
  border-radius: 50%;
  object-fit: cover;
  margin: 0 auto 16px;
  display: block;
  border: 3px solid var(--cv-primary);
}

.cv-sidebar__section {
  margin-bottom: 20px;
}

.cv-sidebar__title {
  font-size: 9pt;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--cv-primary);
  margin-bottom: 8px;
  font-weight: 600;
}

.cv-sidebar__item {
  font-size: 9pt;
  margin-bottom: 4px;
  line-height: 1.4;
}

.cv-sidebar__item--icon {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Main content (right) */
.cv-main {
  flex: 1;
  padding: 20mm 18mm;
}

.cv-main__name {
  font-family: var(--cv-font-heading);
  font-size: 28pt;
  font-weight: 700;
  color: var(--cv-text);
  margin: 0;
  line-height: 1.1;
}

.cv-main__tagline {
  font-size: 12pt;
  color: var(--cv-primary);
  margin-top: 4px;
  margin-bottom: 20px;
}

.cv-section {
  margin-bottom: 18px;
}

.cv-section__title {
  font-size: 11pt;
  font-weight: 700;
  color: var(--cv-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--cv-primary);
  margin-bottom: 10px;
}

/* Timeline entry */
.cv-entry {
  position: relative;
  padding-left: 16px;
  margin-bottom: 14px;
  border-left: 2px solid var(--cv-border);
}

.cv-entry::before {
  content: "";
  position: absolute;
  left: -5px;
  top: 6px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cv-primary);
}

.cv-entry__date {
  font-size: 8.5pt;
  color: var(--cv-text-light);
  font-weight: 600;
}

.cv-entry__title {
  font-weight: 600;
  font-size: 10.5pt;
  margin: 2px 0;
}

.cv-entry__subtitle {
  font-size: 9.5pt;
  color: var(--cv-text-light);
}

.cv-entry__description {
  font-size: 9pt;
  margin-top: 4px;
  color: var(--cv-text);
}
{% endblock %}

{% block page_content %}
<div class="cv-sidebar">
  {% if persoenliche_daten.foto %}
    <img src="{{ persoenliche_daten.foto }}" alt="" class="cv-sidebar__photo">
  {% endif %}

  {# Contact info in sidebar #}
  <div class="cv-sidebar__section">
    <h3 class="cv-sidebar__title">Kontakt</h3>
    <p class="cv-sidebar__item">{{ persoenliche_daten.email }}</p>
    <p class="cv-sidebar__item">{{ persoenliche_daten.telefon }}</p>
    <p class="cv-sidebar__item">{{ persoenliche_daten.strasse }}</p>
    <p class="cv-sidebar__item">{{ persoenliche_daten.plz }} {{ persoenliche_daten.stadt }}</p>
  </div>

  {# Skills in sidebar #}
  {% if kenntnisse %}
  <div class="cv-sidebar__section">
    <h3 class="cv-sidebar__title">Kenntnisse</h3>
    {% for skill in kenntnisse.eintraege %}
      {% include "cv/sections/skill_bar.html" with name=skill.name niveau=skill.niveau light=True %}
    {% endfor %}
  </div>
  {% endif %}

  {# Languages in sidebar #}
  {% if sprachen %}
  <div class="cv-sidebar__section">
    <h3 class="cv-sidebar__title">Sprachen</h3>
    {% for lang in sprachen.eintraege %}
      {% include "cv/sections/language_item.html" with sprache=lang light=True %}
    {% endfor %}
  </div>
  {% endif %}
</div>

<div class="cv-main">
  <h1 class="cv-main__name">{{ persoenliche_daten.vorname }}<br>{{ persoenliche_daten.nachname }}</h1>
  {% if persoenliche_daten.position %}
    <p class="cv-main__tagline">{{ persoenliche_daten.position }}</p>
  {% endif %}

  {# Main sections #}
  {% for section in main_sections %}
    {% if section.is_visible %}
      {% include "cv/sections/"|add:section.section_type|add:".html" with entries=section.content.eintraege %}
    {% endif %}
  {% endfor %}
</div>
{% endblock %}
```

---

## 4. Kreativ Template (Bold Design)

Target: Design, media, creative agencies.

```css
/* templates/cv/kreativ/styles.css */

.cv-page {
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

/* Bold diagonal header */
.cv-header-kreativ {
  background: var(--cv-primary);
  color: white;
  padding: 30mm 25mm 20mm;
  clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
  margin-bottom: -10mm;
}

.cv-header-kreativ__name {
  font-family: var(--cv-font-heading);
  font-size: 32pt;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 0;
}

.cv-header-kreativ__tagline {
  font-size: 14pt;
  font-weight: 300;
  opacity: 0.9;
  margin-top: 4px;
}

/* Circular photo with border */
.cv-photo-kreativ {
  position: absolute;
  top: 15mm;
  right: 25mm;
  width: 45mm;
  height: 45mm;
  border-radius: 50%;
  border: 4px solid white;
  object-fit: cover;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

/* Colored section accent */
.cv-section-kreativ {
  margin: 0 25mm 16px;
}

.cv-section-kreativ__title {
  font-size: 13pt;
  font-weight: 700;
  color: var(--cv-primary);
  display: inline-block;
  padding: 4px 12px;
  background: color-mix(in srgb, var(--cv-primary) 10%, transparent);
  border-radius: 4px;
  margin-bottom: 10px;
}

/* Card-style entries */
.cv-entry-kreativ {
  padding: 10px 14px;
  border-left: 3px solid var(--cv-accent);
  background: var(--cv-surface);
  border-radius: 0 6px 6px 0;
  margin-bottom: 10px;
}
```

---

## 5. Color Theme CSS Custom Properties System

```css
/* static/css/themes.css */

/* ── Default Theme ─────────────────────────────── */
.theme-default {
  --cv-primary: #2563eb;
  --cv-secondary: #64748b;
  --cv-accent: #f59e0b;
  --cv-text: #1e293b;
  --cv-text-light: #64748b;
  --cv-background: #ffffff;
  --cv-surface: #f8fafc;
  --cv-border: #e2e8f0;
}

/* ── Professional Blue ─────────────────────────── */
.theme-professional-blue {
  --cv-primary: #1e3a5f;
  --cv-secondary: #3b6ea5;
  --cv-accent: #d4a843;
  --cv-text: #1a1a2e;
  --cv-text-light: #6b7280;
  --cv-background: #ffffff;
  --cv-surface: #f0f4f8;
  --cv-border: #d1d9e6;
}

/* ── Elegant Dark ──────────────────────────────── */
.theme-elegant-dark {
  --cv-primary: #2d3436;
  --cv-secondary: #636e72;
  --cv-accent: #e17055;
  --cv-text: #2d3436;
  --cv-text-light: #636e72;
  --cv-background: #ffffff;
  --cv-surface: #f5f5f5;
  --cv-border: #dfe6e9;
}

/* ── Modern Teal ───────────────────────────────── */
.theme-modern-teal {
  --cv-primary: #0d9488;
  --cv-secondary: #5eead4;
  --cv-accent: #f59e0b;
  --cv-text: #134e4a;
  --cv-text-light: #64748b;
  --cv-background: #ffffff;
  --cv-surface: #f0fdfa;
  --cv-border: #ccfbf1;
}

/* ── Berry ─────────────────────────────────────── */
.theme-berry {
  --cv-primary: #7c3aed;
  --cv-secondary: #a78bfa;
  --cv-accent: #ec4899;
  --cv-text: #1e1b4b;
  --cv-text-light: #6b7280;
  --cv-background: #ffffff;
  --cv-surface: #faf5ff;
  --cv-border: #e9d5ff;
}

/* ── Forest Green ──────────────────────────────── */
.theme-forest {
  --cv-primary: #166534;
  --cv-secondary: #4ade80;
  --cv-accent: #a16207;
  --cv-text: #14532d;
  --cv-text-light: #6b7280;
  --cv-background: #ffffff;
  --cv-surface: #f0fdf4;
  --cv-border: #bbf7d0;
}

/* ── Warm Red ──────────────────────────────────── */
.theme-warm-red {
  --cv-primary: #991b1b;
  --cv-secondary: #f87171;
  --cv-accent: #d97706;
  --cv-text: #1c1917;
  --cv-text-light: #78716c;
  --cv-background: #ffffff;
  --cv-surface: #fef2f2;
  --cv-border: #fecaca;
}

/* ── Slate Minimal ─────────────────────────────── */
.theme-slate {
  --cv-primary: #334155;
  --cv-secondary: #94a3b8;
  --cv-accent: #334155;
  --cv-text: #0f172a;
  --cv-text-light: #64748b;
  --cv-background: #ffffff;
  --cv-surface: #f8fafc;
  --cv-border: #e2e8f0;
}

/* Sidebar variants for modern template */
.theme-default .cv-sidebar { background: #1e293b; color: #f1f5f9; }
.theme-professional-blue .cv-sidebar { background: #1e3a5f; color: #f0f4f8; }
.theme-elegant-dark .cv-sidebar { background: #2d3436; color: #dfe6e9; }
.theme-modern-teal .cv-sidebar { background: #134e4a; color: #f0fdfa; }
.theme-berry .cv-sidebar { background: #1e1b4b; color: #faf5ff; }
.theme-forest .cv-sidebar { background: #14532d; color: #f0fdf4; }
.theme-warm-red .cv-sidebar { background: #1c1917; color: #fef2f2; }
.theme-slate .cv-sidebar { background: #0f172a; color: #f8fafc; }
```

---

## 6. Font Pairings

```css
/* static/css/fonts.css — Self-hosted @font-face declarations */

/* ── Inter (Modern / Sans-serif) ───────────────── */
@font-face {
  font-family: 'Inter';
  src: url('/static/fonts/inter/Inter-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Inter';
  src: url('/static/fonts/inter/Inter-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Inter';
  src: url('/static/fonts/inter/Inter-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

/* ── Merriweather (Klassisch / Serif) ──────────── */
@font-face {
  font-family: 'Merriweather';
  src: url('/static/fonts/merriweather/Merriweather-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Merriweather';
  src: url('/static/fonts/merriweather/Merriweather-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

/* ── Source Sans Pro (Body text) ───────────────── */
@font-face {
  font-family: 'Source Sans Pro';
  src: url('/static/fonts/source-sans-pro/SourceSansPro-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Source Sans Pro';
  src: url('/static/fonts/source-sans-pro/SourceSansPro-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
  font-display: swap;
}

/* ── Playfair Display (Kreativ / Display Serif) ── */
@font-face {
  font-family: 'Playfair Display';
  src: url('/static/fonts/playfair/PlayfairDisplay-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

/* ── Fira Code (IT/Tech monospace) ─────────────── */
@font-face {
  font-family: 'Fira Code';
  src: url('/static/fonts/fira-code/FiraCode-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
```

### Recommended Font Pairings by Category

| Category | Heading Font | Body Font |
|----------|-------------|-----------|
| Klassisch | Merriweather (serif) | Source Sans Pro |
| Modern | Inter | Inter |
| Kreativ | Playfair Display | Source Sans Pro |
| Akademisch | Merriweather | Source Sans Pro |
| IT/Tech | Inter | Fira Code (for technical) / Inter |
| Student | Inter | Inter |

---

## 7. Section-Specific Design Patterns

### Berufserfahrung Timeline

```html
{# templates/cv/sections/berufserfahrung.html #}

<section class="cv-section">
  <h2 class="cv-section__title">Berufserfahrung</h2>

  {% for eintrag in entries %}
  <div class="cv-entry">
    <div class="cv-entry__date">
      {{ eintrag.von }} –<br>
      {% if eintrag.ist_aktuell %}heute{% else %}{{ eintrag.bis }}{% endif %}
    </div>
    <div class="cv-entry__content">
      <div class="cv-entry__title">{{ eintrag.position }}</div>
      <div class="cv-entry__subtitle">{{ eintrag.unternehmen }}{% if eintrag.ort %}, {{ eintrag.ort }}{% endif %}</div>
      {% if eintrag.aufgaben %}
        <ul class="cv-entry__tasks">
          {% for aufgabe in eintrag.aufgaben %}
            <li>{{ aufgabe }}</li>
          {% endfor %}
        </ul>
      {% elif eintrag.beschreibung %}
        <p class="cv-entry__description">{{ eintrag.beschreibung }}</p>
      {% endif %}
    </div>
  </div>
  {% endfor %}
</section>
```

### Kenntnisse Skill Bars

```html
{# templates/cv/sections/skill_bar.html #}

<div class="cv-skill" style="margin-bottom: 6px;">
  <div class="cv-skill__header" style="display: flex; justify-content: space-between; font-size: 9pt; margin-bottom: 2px;">
    <span class="cv-skill__name">{{ name }}</span>
    <span class="cv-skill__label" style="color: {% if light %}var(--cv-sidebar-text){% else %}var(--cv-text-light){% endif %}; font-size: 8pt;">
      {% if niveau == 1 %}Grundkenntnisse
      {% elif niveau == 2 %}Gute Kenntnisse
      {% elif niveau == 3 %}Fortgeschritten
      {% elif niveau == 4 %}Sehr gut
      {% elif niveau == 5 %}Experte
      {% endif %}
    </span>
  </div>
  <div class="cv-skill__bar" style="height: 4px; background: {% if light %}rgba(255,255,255,0.2){% else %}var(--cv-border){% endif %}; border-radius: 2px; overflow: hidden;">
    <div class="cv-skill__fill" style="height: 100%; width: {{ niveau|multiply:20 }}%; background: var(--cv-primary); border-radius: 2px;"></div>
  </div>
</div>
```

### Alternative: Dot Rating

```html
{# templates/cv/sections/skill_dots.html #}

<div class="cv-skill-dots" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
  <span style="font-size: 9pt;">{{ name }}</span>
  <div style="display: flex; gap: 3px;">
    {% for i in "12345" %}
      <span style="
        width: 8px; height: 8px; border-radius: 50%;
        background: {% if forloop.counter <= niveau %}var(--cv-primary){% else %}var(--cv-border){% endif %};
        display: inline-block;
      "></span>
    {% endfor %}
  </div>
</div>
```

### Sprachen CEFR Levels

```html
{# templates/cv/sections/language_item.html #}

<div class="cv-language" style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 9pt;">
  <span>{{ sprache.sprache }}</span>
  <span style="color: {% if light %}rgba(255,255,255,0.7){% else %}var(--cv-text-light){% endif %};">
    {% if sprache.ist_muttersprache %}
      Muttersprache
    {% else %}
      {{ sprache.niveau }}
      {% if sprache.niveau == "A1" %} — Anfänger
      {% elif sprache.niveau == "A2" %} — Grundlegend
      {% elif sprache.niveau == "B1" %} — Mittelstufe
      {% elif sprache.niveau == "B2" %} — Gute Mittelstufe
      {% elif sprache.niveau == "C1" %} — Fortgeschritten
      {% elif sprache.niveau == "C2" %} — Annähernd muttersprachlich
      {% endif %}
    {% endif %}
  </span>
</div>
```

---

## 8. Photo Placement Options

```css
/* Photo placement variants */

/* Option A: Top-right (Klassisch) */
.photo-top-right .cv-header__photo {
  float: right;
  width: 35mm;
  height: 45mm;
  margin-left: 12px;
  object-fit: cover;
}

/* Option B: Centered above name */
.photo-centered .cv-header__photo {
  display: block;
  width: 40mm;
  height: 50mm;
  margin: 0 auto 12px;
  object-fit: cover;
  border-radius: 4px;
}

/* Option C: Sidebar circle (Modern) */
.photo-sidebar-circle .cv-sidebar__photo {
  width: 50mm;
  height: 50mm;
  border-radius: 50%;
  object-fit: cover;
  display: block;
  margin: 0 auto 16px;
  border: 3px solid var(--cv-primary);
}

/* Option D: Sidebar rounded rectangle */
.photo-sidebar-rounded .cv-sidebar__photo {
  width: 50mm;
  height: 60mm;
  border-radius: 8px;
  object-fit: cover;
  display: block;
  margin: 0 auto 16px;
}
```

---

## 9. Bewerbungsschreiben (Cover Letter) Structure

```html
{# templates/cv/anschreiben/bewerbungsschreiben.html #}

{% extends "cv/base_cv.html" %}

{% block template_css %}
.anschreiben {
  width: 210mm;
  min-height: 297mm;
  padding: 25mm;
  font-family: var(--cv-font-body);
  font-size: 11pt;
  line-height: 1.6;
  color: var(--cv-text);
}

.anschreiben__absender {
  margin-bottom: 8mm;
  font-size: 10pt;
}

.anschreiben__empfaenger {
  margin-bottom: 8mm;
  font-size: 10pt;
}

.anschreiben__ort-datum {
  text-align: right;
  margin-bottom: 8mm;
  font-size: 10pt;
}

.anschreiben__betreff {
  font-weight: 700;
  font-size: 11pt;
  margin-bottom: 6mm;
}

.anschreiben__anrede {
  margin-bottom: 4mm;
}

.anschreiben__text p {
  margin-bottom: 3mm;
  text-align: justify;
  hyphens: auto;
}

.anschreiben__gruss {
  margin-top: 6mm;
}

.anschreiben__unterschrift {
  margin-top: 12mm;
}

.anschreiben__anlagen {
  margin-top: 8mm;
  font-size: 9pt;
  color: var(--cv-text-light);
}
{% endblock %}

{% block page_content %}
<div class="anschreiben">
  {# Sender #}
  <div class="anschreiben__absender">
    {{ absender.vorname }} {{ absender.nachname }}<br>
    {{ absender.strasse }}<br>
    {{ absender.plz }} {{ absender.stadt }}<br>
    {{ absender.telefon }}<br>
    {{ absender.email }}
  </div>

  {# Recipient #}
  <div class="anschreiben__empfaenger">
    {{ empfaenger.firma }}<br>
    {% if empfaenger.ansprechpartner %}{{ empfaenger.ansprechpartner }}<br>{% endif %}
    {{ empfaenger.strasse }}<br>
    {{ empfaenger.plz }} {{ empfaenger.stadt }}
  </div>

  {# City + Date #}
  <div class="anschreiben__ort-datum">
    {{ absender.stadt }}, {{ datum }}
  </div>

  {# Subject line #}
  <div class="anschreiben__betreff">
    {{ betreff }}
  </div>

  {# Salutation #}
  <div class="anschreiben__anrede">
    {{ anrede|default:"Sehr geehrte Damen und Herren," }}
  </div>

  {# Body text #}
  <div class="anschreiben__text">
    {{ text|safe }}
  </div>

  {# Closing #}
  <div class="anschreiben__gruss">
    Mit freundlichen Grüßen
  </div>

  {# Signature #}
  <div class="anschreiben__unterschrift">
    {{ absender.vorname }} {{ absender.nachname }}
  </div>

  {# Attachments #}
  {% if anlagen %}
  <div class="anschreiben__anlagen">
    <strong>Anlagen:</strong><br>
    {% for anlage in anlagen %}
      {{ anlage }}<br>
    {% endfor %}
  </div>
  {% endif %}
</div>
{% endblock %}
```

---

## 10. Deckblatt (Cover Page) Structure

```html
{# templates/cv/deckblatt/deckblatt.html #}

{% extends "cv/base_cv.html" %}

{% block template_css %}
.deckblatt {
  width: 210mm;
  height: 297mm;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-family: var(--cv-font-heading);
  color: var(--cv-text);
  position: relative;
  overflow: hidden;
}

.deckblatt__accent-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8mm;
  background: var(--cv-primary);
}

.deckblatt__accent-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 8mm;
  background: var(--cv-primary);
}

.deckblatt__photo {
  width: 55mm;
  height: 70mm;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 12mm;
  border: 2px solid var(--cv-border);
}

.deckblatt__title {
  font-size: 14pt;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: var(--cv-primary);
  margin-bottom: 6mm;
}

.deckblatt__name {
  font-size: 32pt;
  font-weight: 700;
  margin-bottom: 4mm;
}

.deckblatt__position {
  font-size: 14pt;
  color: var(--cv-text-light);
  margin-bottom: 12mm;
}

.deckblatt__contact {
  font-family: var(--cv-font-body);
  font-size: 10pt;
  color: var(--cv-text-light);
  line-height: 1.8;
}

.deckblatt__stelle {
  font-size: 11pt;
  margin-top: 12mm;
  padding: 4mm 8mm;
  border: 1px solid var(--cv-border);
  border-radius: 4px;
  color: var(--cv-text-light);
}
{% endblock %}

{% block page_content %}
<div class="deckblatt">
  <div class="deckblatt__accent-top"></div>

  {% if persoenliche_daten.foto %}
    <img src="{{ persoenliche_daten.foto }}" alt="" class="deckblatt__photo">
  {% endif %}

  <div class="deckblatt__title">Bewerbung</div>
  <div class="deckblatt__name">{{ persoenliche_daten.vorname }} {{ persoenliche_daten.nachname }}</div>

  {% if bewerbung.position %}
    <div class="deckblatt__position">{{ bewerbung.position }}</div>
  {% endif %}

  <div class="deckblatt__contact">
    {{ persoenliche_daten.strasse }}<br>
    {{ persoenliche_daten.plz }} {{ persoenliche_daten.stadt }}<br>
    {{ persoenliche_daten.telefon }}<br>
    {{ persoenliche_daten.email }}
  </div>

  {% if bewerbung.stelle %}
    <div class="deckblatt__stelle">
      Bewerbung als: {{ bewerbung.stelle }}
      {% if bewerbung.firma %}<br>bei {{ bewerbung.firma }}{% endif %}
    </div>
  {% endif %}

  <div class="deckblatt__accent-bottom"></div>
</div>
{% endblock %}
```
