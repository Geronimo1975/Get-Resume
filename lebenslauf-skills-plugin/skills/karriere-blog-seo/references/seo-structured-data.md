# SEO Structured Data and Meta Templates Reference

## Overview

This reference documents all SEO-related templates and configurations for the Lebenslauf-Builder platform, including JSON-LD structured data, meta tags, robots.txt, XML sitemap format, hreflang implementation, and CTA widget templates. All structured data follows schema.org vocabulary and Google's guidelines for rich results.

---

## 1. JSON-LD Structured Data Templates

### Organization

```html
{# seo/templates/seo/jsonld/organization.html #}

{# Included on every page via base.html #}
{# Provides Google Knowledge Panel eligibility #}

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": "{{ site_url }}/#organization",
    "name": "Lebenslauf-Builder",
    "legalName": "Lebenslauf-Builder GmbH",
    "url": "{{ site_url }}/",
    "logo": {
        "@type": "ImageObject",
        "url": "{{ site_url }}{% static 'images/logo.png' %}",
        "width": 512,
        "height": 512
    },
    "image": "{{ site_url }}{% static 'images/og-default.jpg' %}",
    "description": "Professionellen Lebenslauf online erstellen. Kostenlose Vorlagen, DSGVO-konform, made in Germany.",
    "foundingDate": "2024",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Musterstrasse 42",
        "addressLocality": "Berlin",
        "postalCode": "10115",
        "addressCountry": "DE"
    },
    "contactPoint": [
        {
            "@type": "ContactPoint",
            "telephone": "+49-30-1234567",
            "contactType": "customer service",
            "availableLanguage": ["German", "English"],
            "areaServed": ["DE", "AT", "CH"]
        }
    ],
    "sameAs": [
        "https://www.linkedin.com/company/lebenslauf-builder",
        "https://www.xing.com/pages/lebenslauf-builder",
        "https://twitter.com/LebenslaufBuild"
    ],
    "vatID": "DE123456789",
    "taxID": "27/123/45678"
}
</script>
```

### Product + Offer (with EUR MwSt Pricing)

```html
{# seo/templates/seo/jsonld/product_offer.html #}

{# Included on the pricing page (/preise/) #}
{# Shows pricing in Google search results #}

{% for plan in plans %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Lebenslauf-Builder {{ plan.display_name }}",
    "description": "{{ plan.description }}",
    "brand": {
        "@type": "Organization",
        "name": "Lebenslauf-Builder"
    },
    "image": "{{ site_url }}{% static 'images/plans/' %}{{ plan.slug }}.png",
    "url": "{{ site_url }}/preise/#{{ plan.slug }}",
    "offers": {
        "@type": "Offer",
        "url": "{{ site_url }}/preise/#{{ plan.slug }}",
        "priceCurrency": "EUR",
        "price": "{{ plan.price_monthly_brutto }}",
        "priceValidUntil": "{{ price_valid_until|date:'Y-m-d' }}",
        "availability": "https://schema.org/InStock",
        "itemCondition": "https://schema.org/NewCondition",
        "seller": {
            "@type": "Organization",
            "@id": "{{ site_url }}/#organization"
        },
        "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "price": "{{ plan.price_monthly_brutto }}",
            "priceCurrency": "EUR",
            "unitCode": "MON",
            "referenceQuantity": {
                "@type": "QuantitativeValue",
                "value": "1",
                "unitCode": "MON"
            },
            "valueAddedTaxIncluded": true,
            "valueAddedTaxPercentage": 19
        },
        "hasMerchantReturnPolicy": {
            "@type": "MerchantReturnPolicy",
            "applicableCountry": "DE",
            "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
            "merchantReturnDays": 14,
            "returnMethod": "https://schema.org/ReturnByMail",
            "returnFees": "https://schema.org/FreeReturn"
        }
    },
    "review": {
        "@type": "Review",
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": "{{ plan.avg_rating|default:'4.8' }}",
            "bestRating": "5"
        },
        "author": {
            "@type": "Organization",
            "name": "Lebenslauf-Builder Redaktion"
        }
    },
    "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "{{ plan.avg_rating|default:'4.8' }}",
        "reviewCount": "{{ plan.review_count|default:'127' }}",
        "bestRating": "5",
        "worstRating": "1"
    }
}
</script>
{% endfor %}
```

### FAQPage

```html
{# seo/templates/seo/jsonld/faq_page.html #}

{# Included on FAQ sections of landing pages #}
{# Generates FAQ rich snippets in Google SERPs #}

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {% for faq in faqs %}
        {
            "@type": "Question",
            "name": "{{ faq.question|escapejs }}",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "{{ faq.answer|escapejs }}"
            }
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]
}
</script>

{# Example FAQ data for pricing page:
faqs = [
    {
        "question": "Was kostet der Lebenslauf-Builder?",
        "answer": "Der Lebenslauf-Builder bietet einen kostenlosen Plan mit Grundfunktionen. Premium-Plaene starten ab 4,99 EUR/Monat (inkl. 19% MwSt.) mit erweiterten Vorlagen und PDF-Export."
    },
    {
        "question": "Kann ich den Lebenslauf-Builder kostenlos testen?",
        "answer": "Ja, der kostenlose Plan ist zeitlich unbegrenzt. Sie koennen bis zu 3 Dokumente erstellen und als PDF herunterladen. Fuer Premium-Funktionen gibt es eine 14-taegige Geld-zurueck-Garantie."
    },
    {
        "question": "Ist der Lebenslauf-Builder DSGVO-konform?",
        "answer": "Ja, der Lebenslauf-Builder ist vollstaendig DSGVO-konform. Alle Daten werden auf Servern in Deutschland (Hetzner, Nuernberg) gespeichert. Sie koennen Ihre Daten jederzeit exportieren oder loeschen lassen."
    },
    {
        "question": "Kann ich mein Abo jederzeit kuendigen?",
        "answer": "Ja, Sie koennen Ihr Abo jederzeit kuendigen. Die Kuendigung wird zum Ende des aktuellen Abrechnungszeitraums wirksam. Innerhalb der ersten 14 Tage haben Sie ein gesetzliches Widerrufsrecht mit voller Erstattung."
    },
    {
        "question": "Welche Zahlungsmethoden werden akzeptiert?",
        "answer": "Wir akzeptieren Kreditkarte (Visa, Mastercard), SEPA-Lastschrift und giropay. Alle Zahlungen werden sicher ueber Stripe abgewickelt."
    },
]
#}
```

### BlogPosting

```html
{# seo/templates/seo/jsonld/blog_posting.html #}

{# Included on blog article detail pages #}
{# Generates Article rich snippets with author info (E-E-A-T) #}

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "@id": "{{ site_url }}{{ article.get_absolute_url }}",
    "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "{{ site_url }}{{ article.get_absolute_url }}"
    },
    "headline": "{{ article.title|escapejs }}",
    "description": "{{ article.get_meta_description|escapejs }}",
    "datePublished": "{{ article.published_at|date:'c' }}",
    "dateModified": "{{ article.updated_at|date:'c' }}",
    "wordCount": {{ article.word_count }},
    "timeRequired": "PT{{ article.reading_time_minutes }}M",
    {% if article.featured_image %}
    "image": {
        "@type": "ImageObject",
        "url": "{{ site_url }}{{ article.featured_image.url }}",
        "caption": "{{ article.featured_image_alt|escapejs }}"
    },
    {% endif %}
    "author": {
        "@type": "Person",
        "name": "{{ article.author.name|escapejs }}",
        "url": "{{ site_url }}{{ article.author.get_absolute_url }}",
        {% if article.author.photo %}
        "image": "{{ site_url }}{{ article.author.photo.url }}",
        {% endif %}
        {% if article.author.linkedin_url %}
        "sameAs": ["{{ article.author.linkedin_url }}"{% if article.author.xing_url %}, "{{ article.author.xing_url }}"{% endif %}],
        {% endif %}
        "jobTitle": "{{ article.author.expertise.0|default:'Karriereberater' }}",
        "description": "{{ article.author.bio_short|escapejs }}"
    },
    "publisher": {
        "@type": "Organization",
        "@id": "{{ site_url }}/#organization"
    },
    "articleSection": "{{ article.category.name|escapejs }}",
    "keywords": "{% for tag in article.tags.all %}{{ tag.name }}{% if not forloop.last %}, {% endif %}{% endfor %}",
    "inLanguage": "de-DE",
    "isAccessibleForFree": true,
    "isPartOf": {
        "@type": "Blog",
        "@id": "{{ site_url }}/karriere-blog/#blog",
        "name": "Lebenslauf-Builder Karriere-Blog",
        "url": "{{ site_url }}/karriere-blog/"
    }
    {% if article.is_pillar_article %},
    "about": {
        "@type": "Thing",
        "name": "{{ article.category.name|escapejs }}"
    }
    {% endif %}
}
</script>
```

### HowTo

```html
{# seo/templates/seo/jsonld/how_to.html #}

{# Included on articles tagged as how-to guides #}
{# Generates HowTo rich snippets with step-by-step instructions #}

<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": "{{ howto.title|escapejs }}",
    "description": "{{ howto.description|escapejs }}",
    "image": "{{ site_url }}{{ howto.image_url }}",
    "totalTime": "PT{{ howto.total_time_minutes }}M",
    "estimatedCost": {
        "@type": "MonetaryAmount",
        "currency": "EUR",
        "value": "{{ howto.cost|default:'0' }}"
    },
    {% if howto.tools %}
    "tool": [
        {% for tool in howto.tools %}
        {
            "@type": "HowToTool",
            "name": "{{ tool|escapejs }}"
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ],
    {% endif %}
    {% if howto.supplies %}
    "supply": [
        {% for supply in howto.supplies %}
        {
            "@type": "HowToSupply",
            "name": "{{ supply|escapejs }}"
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ],
    {% endif %}
    "step": [
        {% for step in howto.steps %}
        {
            "@type": "HowToStep",
            "position": {{ forloop.counter }},
            "name": "{{ step.title|escapejs }}",
            "text": "{{ step.text|escapejs }}",
            "url": "{{ site_url }}{{ howto.url }}#schritt-{{ forloop.counter }}"
            {% if step.image %},
            "image": "{{ site_url }}{{ step.image }}"
            {% endif %}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]
}
</script>

{# Example usage on a "Lebenslauf schreiben" article:
howto = {
    "title": "Lebenslauf schreiben: Schritt-fuer-Schritt Anleitung",
    "description": "Erfahren Sie, wie Sie in 7 einfachen Schritten einen professionellen Lebenslauf erstellen.",
    "image_url": "/static/images/blog/lebenslauf-schreiben-howto.jpg",
    "total_time_minutes": 30,
    "cost": "0",
    "tools": ["Computer oder Smartphone", "Lebenslauf-Builder (kostenlos)"],
    "supplies": ["Berufserfahrung und Ausbildungsdaten", "Professionelles Foto"],
    "url": "/karriere-blog/lebenslauf-schreiben-anleitung/",
    "steps": [
        {"title": "Vorlage auswaehlen", "text": "Waehlen Sie eine professionelle Vorlage..."},
        {"title": "Persoenliche Daten eingeben", "text": "Tragen Sie Ihren Namen, Adresse..."},
        ...
    ],
}
#}
```

### BreadcrumbList

```html
{# seo/templates/seo/jsonld/breadcrumbs.html #}

{# Included on every page with breadcrumb navigation #}
{# Generates breadcrumb trail in Google SERPs #}

{% if breadcrumbs %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Startseite",
            "item": "{{ site_url }}/"
        }{% if breadcrumbs %},{% endif %}
        {% for crumb in breadcrumbs %}
        {
            "@type": "ListItem",
            "position": {{ forloop.counter|add:1 }},
            "name": "{{ crumb.name|escapejs }}"
            {% if crumb.url %},
            "item": "{{ site_url }}{{ crumb.url }}"
            {% endif %}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]
}
</script>
{% endif %}
```

---

## 2. Meta Tag Template

```html
{# seo/templates/seo/meta_tags.html #}

{# Include in <head> of every page via: {% include "seo/meta_tags.html" %} #}
{# Expects 'seo' context variable with SEOMixin fields, or individual vars #}

{# === Basic Meta Tags === #}
<title>{% block seo_title %}{% if seo %}{{ seo.get_meta_title }}{% elif page_meta_title %}{{ page_meta_title }}{% else %}Lebenslauf-Builder - Professionellen Lebenslauf online erstellen{% endif %}{% endblock %}</title>

<meta name="description" content="{% block seo_description %}{% if seo %}{{ seo.get_meta_description }}{% elif page_meta_description %}{{ page_meta_description }}{% else %}Erstellen Sie Ihren professionellen Lebenslauf in Minuten. Kostenlose Vorlagen, DSGVO-konform, PDF-Export. Made in Germany.{% endif %}{% endblock %}">

{# === Robots === #}
<meta name="robots" content="{% if seo %}{{ seo.get_robots_meta }}{% elif noindex %}noindex, nofollow{% else %}index, follow{% endif %}">

{# === Canonical URL === #}
{% if seo and seo.canonical_url %}
<link rel="canonical" href="{{ seo.canonical_url }}">
{% elif canonical_url %}
<link rel="canonical" href="{{ canonical_url }}">
{% else %}
<link rel="canonical" href="{{ site_url }}{{ request.path }}">
{% endif %}

{# === Open Graph (Facebook, LinkedIn) === #}
<meta property="og:type" content="{% if article %}article{% else %}website{% endif %}">
<meta property="og:title" content="{% if seo %}{{ seo.get_meta_title }}{% elif page_meta_title %}{{ page_meta_title }}{% else %}Lebenslauf-Builder{% endif %}">
<meta property="og:description" content="{% if seo %}{{ seo.get_meta_description }}{% elif page_meta_description %}{{ page_meta_description }}{% else %}Professionellen Lebenslauf online erstellen.{% endif %}">
<meta property="og:url" content="{{ site_url }}{{ request.path }}">
<meta property="og:site_name" content="Lebenslauf-Builder">
<meta property="og:locale" content="de_DE">

{% if seo and seo.get_og_image_url %}
<meta property="og:image" content="{{ site_url }}{{ seo.get_og_image_url }}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{% elif og_image %}
<meta property="og:image" content="{{ site_url }}{{ og_image }}">
{% else %}
<meta property="og:image" content="{{ site_url }}{% static 'images/og-default.jpg' %}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{% endif %}

<meta property="og:image:alt" content="{% if seo %}{{ seo.get_meta_title }}{% else %}Lebenslauf-Builder{% endif %}">

{# Article-specific OG tags #}
{% if article %}
<meta property="article:published_time" content="{{ article.published_at|date:'c' }}">
<meta property="article:modified_time" content="{{ article.updated_at|date:'c' }}">
<meta property="article:section" content="{{ article.category.name }}">
<meta property="article:author" content="{{ article.author.name }}">
{% for tag in article.tags.all %}
<meta property="article:tag" content="{{ tag.name }}">
{% endfor %}
{% endif %}

{# === Twitter Card === #}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@LebenslaufBuild">
<meta name="twitter:title" content="{% if seo %}{{ seo.get_meta_title }}{% elif page_meta_title %}{{ page_meta_title }}{% else %}Lebenslauf-Builder{% endif %}">
<meta name="twitter:description" content="{% if seo %}{{ seo.get_meta_description }}{% elif page_meta_description %}{{ page_meta_description }}{% else %}Professionellen Lebenslauf online erstellen.{% endif %}">

{% if seo and seo.get_og_image_url %}
<meta name="twitter:image" content="{{ site_url }}{{ seo.get_og_image_url }}">
{% else %}
<meta name="twitter:image" content="{{ site_url }}{% static 'images/og-default.jpg' %}">
{% endif %}

{# === hreflang (DE/EN) === #}
{% block hreflang %}
<link rel="alternate" hreflang="de" href="{{ site_url }}{{ request.path }}">
<link rel="alternate" hreflang="en" href="{{ site_url }}/en{{ request.path }}">
<link rel="alternate" hreflang="x-default" href="{{ site_url }}{{ request.path }}">
{% endblock %}

{# === Additional meta === #}
<meta name="author" content="{% if article %}{{ article.author.name }}{% else %}Lebenslauf-Builder GmbH{% endif %}">
<meta name="publisher" content="Lebenslauf-Builder GmbH">
<meta name="language" content="de">
<meta name="geo.region" content="DE">
<meta name="geo.placename" content="Berlin">

{# === RSS feed auto-discovery === #}
<link rel="alternate" type="application/rss+xml" title="Karriere-Blog RSS Feed" href="{{ site_url }}/karriere-blog/feed/rss/">

{# === Favicon === #}
<link rel="icon" type="image/svg+xml" href="{% static 'images/favicon.svg' %}">
<link rel="apple-touch-icon" href="{% static 'images/apple-touch-icon.png' %}">
<link rel="manifest" href="{% static 'site.webmanifest' %}">
```

---

## 3. robots.txt

```python
# seo/views.py

from django.http import HttpResponse
from django.views import View


class RobotsTxtView(View):
    """
    Serve robots.txt dynamically based on environment.

    URL: /robots.txt
    """

    def get(self, request):
        from django.conf import settings

        if settings.ENVIRONMENT == "production":
            content = """# robots.txt for Lebenslauf-Builder
# https://www.lebenslauf-builder.de/robots.txt

User-agent: *
Allow: /
Allow: /karriere-blog/
Allow: /lebenslauf-vorlagen/
Allow: /anschreiben-vorlagen/
Allow: /preise/

# Disallow dashboard and private areas
Disallow: /dashboard/
Disallow: /admin/
Disallow: /api/
Disallow: /accounts/
Disallow: /editor/
Disallow: /webhooks/
Disallow: /health/

# Disallow search result pages
Disallow: /karriere-blog/?q=
Disallow: /karriere-blog/?page=

# Disallow print/PDF views
Disallow: /*/print/
Disallow: /*/pdf/

# Rate limiting for crawlers
Crawl-delay: 1

# Sitemap location
Sitemap: https://www.lebenslauf-builder.de/sitemap.xml
Sitemap: https://www.lebenslauf-builder.de/sitemap-blog.xml

# Special rules for specific bots
User-agent: GPTBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: anthropic-ai
Disallow: /
"""
        else:
            # Staging/development: disallow all crawling
            content = """# robots.txt - Non-production environment
User-agent: *
Disallow: /
"""

        return HttpResponse(content, content_type="text/plain")
```

---

## 4. XML Sitemap Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
    Lebenslauf-Builder Sitemap
    Generated by: python manage.py generate_sitemap
    Regenerated daily via Celery beat task

    Follows the Sitemaps.org XML protocol:
    https://www.sitemaps.org/protocol.html

    Includes:
    - Image sitemap extension
    - hreflang annotations for DE/EN
-->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">

    <!-- Homepage -->
    <url>
        <loc>https://www.lebenslauf-builder.de/</loc>
        <lastmod>2026-03-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
        <xhtml:link rel="alternate" hreflang="de" href="https://www.lebenslauf-builder.de/"/>
        <xhtml:link rel="alternate" hreflang="en" href="https://www.lebenslauf-builder.de/en/"/>
        <xhtml:link rel="alternate" hreflang="x-default" href="https://www.lebenslauf-builder.de/"/>
    </url>

    <!-- Static pages -->
    <url>
        <loc>https://www.lebenslauf-builder.de/preise/</loc>
        <lastmod>2026-02-15</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
        <xhtml:link rel="alternate" hreflang="de" href="https://www.lebenslauf-builder.de/preise/"/>
        <xhtml:link rel="alternate" hreflang="en" href="https://www.lebenslauf-builder.de/en/pricing/"/>
    </url>

    <!-- Blog articles -->
    <url>
        <loc>https://www.lebenslauf-builder.de/karriere-blog/lebenslauf-schreiben-anleitung/</loc>
        <lastmod>2026-02-28</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
        <image:image>
            <image:loc>https://www.lebenslauf-builder.de/media/blog/featured/2026/02/lebenslauf-anleitung.jpg</image:loc>
            <image:caption>Lebenslauf schreiben - Schritt-fuer-Schritt Anleitung</image:caption>
            <image:title>Lebenslauf schreiben Anleitung</image:title>
        </image:image>
    </url>

    <!-- Categories -->
    <url>
        <loc>https://www.lebenslauf-builder.de/karriere-blog/kategorie/lebenslauf-tipps/</loc>
        <lastmod>2026-02-28</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>

    <!-- Template pages -->
    <url>
        <loc>https://www.lebenslauf-builder.de/lebenslauf-vorlagen/</loc>
        <lastmod>2026-02-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
        <image:image>
            <image:loc>https://www.lebenslauf-builder.de/static/images/templates/modern-preview.jpg</image:loc>
            <image:caption>Moderne Lebenslauf-Vorlage</image:caption>
        </image:image>
    </url>
</urlset>
```

### Sitemap Index (for large sites)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
    Sitemap Index when individual sitemaps exceed 50,000 URLs
    or 50MB uncompressed.
-->
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://www.lebenslauf-builder.de/sitemap-pages.xml</loc>
        <lastmod>2026-03-01</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.lebenslauf-builder.de/sitemap-blog.xml</loc>
        <lastmod>2026-03-01</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.lebenslauf-builder.de/sitemap-templates.xml</loc>
        <lastmod>2026-02-20</lastmod>
    </sitemap>
</sitemapindex>
```

---

## 5. hreflang Implementation for DE/EN

```python
# seo/middleware.py

class HreflangMiddleware:
    """
    Middleware that adds hreflang context data for templates.

    The Lebenslauf-Builder supports two languages:
    - de (default): German - primary market (DE, AT, CH)
    - en: English - secondary market

    URL structure:
    - German: /karriere-blog/lebenslauf-tipps/
    - English: /en/career-blog/resume-tips/

    hreflang tells Google which version to show in which market.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        """Add hreflang URLs to template context."""
        if not hasattr(response, "context_data"):
            return response

        site_url = "https://www.lebenslauf-builder.de"
        current_path = request.path

        # Determine current language
        is_english = current_path.startswith("/en/")

        if is_english:
            # Current is EN, generate DE alternate
            de_path = current_path.replace("/en/", "/", 1)
            en_path = current_path
        else:
            # Current is DE, generate EN alternate
            de_path = current_path
            en_path = f"/en{current_path}"

        hreflang_data = {
            "hreflang_de": f"{site_url}{de_path}",
            "hreflang_en": f"{site_url}{en_path}",
            "hreflang_default": f"{site_url}{de_path}",
        }

        if response.context_data is not None:
            response.context_data.update(hreflang_data)

        return response
```

### hreflang HTML Implementation

```html
{# In base.html <head> section #}

{# Link rel="alternate" hreflang tags for all supported languages #}
<link rel="alternate" hreflang="de" href="{{ hreflang_de }}">
<link rel="alternate" hreflang="en" href="{{ hreflang_en }}">
<link rel="alternate" hreflang="x-default" href="{{ hreflang_default }}">

{# HTTP Header alternative (set via middleware for non-HTML responses) #}
{# Link: <https://www.lebenslauf-builder.de/preise/>; rel="alternate"; hreflang="de",
         <https://www.lebenslauf-builder.de/en/pricing/>; rel="alternate"; hreflang="en" #}
```

### URL Mapping for DE/EN

```python
# seo/url_mapping.py

"""
Mapping between German and English URL paths for hreflang.

Used by the HreflangMiddleware and sitemap generator to create
correct alternate URL references.
"""

URL_TRANSLATIONS = {
    # Static pages
    "/": "/en/",
    "/preise/": "/en/pricing/",
    "/lebenslauf-vorlagen/": "/en/resume-templates/",
    "/anschreiben-vorlagen/": "/en/cover-letter-templates/",
    "/karriere-blog/": "/en/career-blog/",
    "/ueber-uns/": "/en/about-us/",
    "/kontakt/": "/en/contact/",
    "/impressum/": "/en/legal-notice/",
    "/datenschutz/": "/en/privacy-policy/",
    "/agb/": "/en/terms-of-service/",
    "/widerruf/": "/en/cancellation-policy/",

    # Blog categories
    "/karriere-blog/kategorie/lebenslauf-tipps/": "/en/career-blog/category/resume-tips/",
    "/karriere-blog/kategorie/bewerbung-schreiben/": "/en/career-blog/category/application-writing/",
    "/karriere-blog/kategorie/vorstellungsgespraech/": "/en/career-blog/category/job-interview/",
    "/karriere-blog/kategorie/karriereplanung/": "/en/career-blog/category/career-planning/",
}
```

---

## 6. CTA Widget Templates

### Sidebar CTA Widget

```html
{# seo/templates/seo/widgets/cta_sidebar.html #}

{# Sticky sidebar CTA widget for blog pages #}
{# Placed in the blog sidebar, sticky on scroll #}

<div class="cta-sidebar-widget" id="cta-sidebar">
    <div class="cta-widget-card">
        {# Gradient background header #}
        <div class="cta-widget-header">
            <h3 class="cta-widget-title">
                Professionellen Lebenslauf erstellen
            </h3>
            <p class="cta-widget-subtitle">
                In nur 10 Minuten zum perfekten Lebenslauf
            </p>
        </div>

        <div class="cta-widget-body">
            {# Bullet points #}
            <ul class="cta-feature-list">
                <li>
                    <svg class="cta-check-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span>20+ professionelle Vorlagen</span>
                </li>
                <li>
                    <svg class="cta-check-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span>PDF-Export in Sekunden</span>
                </li>
                <li>
                    <svg class="cta-check-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span>100% DSGVO-konform</span>
                </li>
                <li>
                    <svg class="cta-check-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                    </svg>
                    <span>Kostenlos starten</span>
                </li>
            </ul>

            {# CTA Button #}
            <a href="/registrieren/?utm_source=blog&utm_medium=sidebar_cta&utm_campaign={{ article.category.slug|default:'general' }}"
               class="cta-widget-button">
                Jetzt kostenlos starten
            </a>

            {# Trust signals #}
            <div class="cta-trust-signals">
                <span class="cta-trust-item">
                    <svg width="12" height="12" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                    4.8/5 Bewertung
                </span>
                <span class="cta-trust-item">
                    50.000+ Nutzer
                </span>
            </div>
        </div>
    </div>
</div>

<style>
.cta-sidebar-widget {
    position: sticky;
    top: 20px;
}

.cta-widget-card {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
}

.cta-widget-header {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    padding: 20px;
    color: white;
}

.cta-widget-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.cta-widget-subtitle {
    font-size: 0.85rem;
    opacity: 0.9;
    margin: 0;
}

.cta-widget-body {
    padding: 20px;
    background: white;
}

.cta-feature-list {
    list-style: none;
    padding: 0;
    margin: 0 0 16px;
}

.cta-feature-list li {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    font-size: 0.9rem;
}

.cta-check-icon {
    color: #16a34a;
    flex-shrink: 0;
}

.cta-widget-button {
    display: block;
    width: 100%;
    padding: 12px;
    background: #2563eb;
    color: white;
    text-align: center;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
}

.cta-widget-button:hover {
    background: #1d4ed8;
    color: white;
}

.cta-trust-signals {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 12px;
    font-size: 0.8rem;
    color: #6b7280;
}

.cta-trust-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

.cta-trust-item svg {
    color: #f59e0b;
}
</style>
```

### Inline CTA Widget (Within Article Content)

```html
{# seo/templates/seo/widgets/cta_inline.html #}

{# Placed within blog article content, typically after the 3rd paragraph #}
{# Use Django template tag: {% include "seo/widgets/cta_inline.html" %} #}

<div class="cta-inline-widget" role="complementary" aria-label="Angebot">
    <div class="cta-inline-inner">
        <div class="cta-inline-content">
            <div class="cta-inline-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"
                     fill="currentColor" viewBox="0 0 16 16">
                    <path d="M9.293 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.707A1 1 0 0 0 13.707 4L10 .293A1 1 0 0 0 9.293 0z"/>
                </svg>
            </div>
            <div>
                <h4 class="cta-inline-title">
                    Lebenslauf direkt erstellen?
                </h4>
                <p class="cta-inline-text">
                    Mit dem Lebenslauf-Builder erstellen Sie in Minuten einen
                    professionellen Lebenslauf. Kostenlos und ohne Anmeldung testen.
                </p>
            </div>
        </div>
        <a href="/registrieren/?utm_source=blog&utm_medium=inline_cta&utm_campaign={{ article.category.slug|default:'general' }}"
           class="cta-inline-button">
            Kostenlos testen
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                 fill="currentColor" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
            </svg>
        </a>
    </div>
</div>

<style>
.cta-inline-widget {
    margin: 32px 0;
    padding: 24px;
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border-radius: 12px;
    border-left: 4px solid #2563eb;
}

.cta-inline-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    flex-wrap: wrap;
}

.cta-inline-content {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    flex: 1;
}

.cta-inline-icon {
    color: #2563eb;
    flex-shrink: 0;
}

.cta-inline-title {
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 4px;
    color: #1e293b;
}

.cta-inline-text {
    font-size: 0.9rem;
    color: #475569;
    margin: 0;
}

.cta-inline-button {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: #2563eb;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none;
    white-space: nowrap;
    transition: background 0.2s, transform 0.1s;
    flex-shrink: 0;
}

.cta-inline-button:hover {
    background: #1d4ed8;
    color: white;
    transform: translateX(2px);
}

@media (max-width: 640px) {
    .cta-inline-inner {
        flex-direction: column;
        align-items: stretch;
    }
    .cta-inline-button {
        text-align: center;
        justify-content: center;
    }
}
</style>
```

### Template Tag for Auto-Inserting CTA into Content

```python
# seo/templatetags/seo_tags.py

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.simple_tag(takes_context=True)
def render_content_with_cta(context, content, insert_after_paragraph=3):
    """
    Render article content with inline CTA widget inserted after
    the Nth paragraph.

    Usage:
        {% load seo_tags %}
        {% render_content_with_cta article.content_html 3 %}

    Args:
        content: HTML content string
        insert_after_paragraph: Paragraph number after which to insert CTA
    """
    cta_html = render_to_string(
        "seo/widgets/cta_inline.html",
        context.flatten(),
    )

    # Find the Nth closing </p> tag and insert CTA after it
    paragraphs_found = 0
    insert_position = 0

    for match in re.finditer(r"</p>", content):
        paragraphs_found += 1
        if paragraphs_found == insert_after_paragraph:
            insert_position = match.end()
            break

    if insert_position > 0:
        content = content[:insert_position] + cta_html + content[insert_position:]

    return mark_safe(content)
```
