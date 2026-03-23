# Rendering Engine Reference

WeasyPrint PDF rendering engine, template models, print CSS, preview rendering, and caching strategy.

---

## 1. PDF Rendering Service

```python
# documents/services.py

import io
import logging
from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class PDFRenderingService:
    """
    Renders CV documents to PDF using WeasyPrint.

    Usage:
        service = PDFRenderingService()
        pdf_bytes = service.render_to_pdf(document)
        # or
        service.render_and_save(document)  # saves to document.pdf_file
    """

    # A4 dimensions
    PAGE_WIDTH_MM = 210
    PAGE_HEIGHT_MM = 297

    # Default margins
    MARGIN_TOP_MM = 15
    MARGIN_BOTTOM_MM = 15
    MARGIN_LEFT_MM = 20
    MARGIN_RIGHT_MM = 20

    def __init__(self):
        self.font_config = FontConfiguration()
        self.base_url = getattr(settings, "WEASYPRINT_BASEURL", "http://localhost:8000")
        self.fonts_dir = Path(settings.STATIC_ROOT) / "fonts"

    def render_to_pdf(self, document):
        """
        Render a Document model instance to PDF bytes.

        Args:
            document: Document model instance with template, sections, and theme

        Returns:
            bytes: PDF file content
        """
        # Build the full HTML
        html_content = self._build_html(document)

        # Build CSS (template CSS + print CSS + font CSS)
        css_content = self._build_css(document)

        # Render with WeasyPrint
        try:
            html = HTML(
                string=html_content,
                base_url=self.base_url,
            )
            css = CSS(
                string=css_content,
                font_config=self.font_config,
            )

            pdf_bytes = html.write_pdf(
                stylesheets=[css],
                font_config=self.font_config,
                presentational_hints=True,
            )

            logger.info(
                "PDF rendered for document %s (%d bytes)",
                document.id,
                len(pdf_bytes),
            )
            return pdf_bytes

        except Exception:
            logger.exception("PDF rendering failed for document %s", document.id)
            raise

    def render_and_save(self, document):
        """
        Render PDF and save to the document's pdf_file field.
        Invalidates any existing cached PDF first.
        """
        # Remove old cached PDF
        if document.pdf_file:
            document.pdf_file.delete(save=False)

        # Render new PDF
        pdf_bytes = self.render_to_pdf(document)

        # Save to FileField
        filename = f"{document.id}.pdf"
        document.pdf_file.save(
            filename,
            ContentFile(pdf_bytes),
            save=True,
        )

        logger.info("PDF saved for document %s", document.id)
        return document.pdf_file

    def render_to_html(self, document):
        """
        Render document to HTML string only (for editor preview).
        No PDF generation — much faster for live preview.
        """
        html_content = self._build_html(document)
        css_content = self._build_css(document)

        # Wrap in full HTML with embedded CSS
        return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <style>{self._get_font_css()}</style>
    <style>{css_content}</style>
</head>
<body>
    {html_content}
</body>
</html>"""

    def _build_html(self, document):
        """Build the full HTML content for a document."""
        template = document.template

        if not template:
            logger.warning("Document %s has no template, using default", document.id)
            template_path = "cv/klassisch/lebenslauf.html"
        else:
            template_path = f"cv/{template.slug}/lebenslauf.html"

        # Gather section data
        sections = document.sections.filter(is_visible=True).order_by("ordering")
        section_data = {}
        for section in sections:
            section_data[section.section_type] = section.content

        # Prepare template context
        context = {
            "document": document,
            "template": template,
            "sections": sections,
            "persoenliche_daten": section_data.get("persoenliche_daten", {}),
            "berufserfahrung": section_data.get("berufserfahrung", {}),
            "ausbildung": section_data.get("ausbildung", {}),
            "kenntnisse": section_data.get("kenntnisse", {}),
            "sprachen": section_data.get("sprachen", {}),
            "weiterbildungen": section_data.get("weiterbildungen", {}),
            "ehrenamt": section_data.get("ehrenamt", {}),
            "interessen": section_data.get("interessen", {}),
            "unterschrift": section_data.get("unterschrift", {}),
            "theme": self._resolve_theme(document.theme),
            # For Berufserfahrung/Ausbildung main section listing
            "main_sections": sections.exclude(
                section_type__in=["persoenliche_daten", "unterschrift"]
            ),
        }

        try:
            return render_to_string(template_path, context)
        except Exception:
            logger.exception("Template rendering failed: %s", template_path)
            # Fallback to klassisch
            return render_to_string("cv/klassisch/lebenslauf.html", context)

    def _build_css(self, document):
        """Build combined CSS for the document."""
        parts = []

        # 1. Font declarations
        parts.append(self._get_font_css())

        # 2. Print CSS (page rules)
        parts.append(self._get_print_css())

        # 3. Template-specific CSS
        if document.template and document.template.css_template:
            parts.append(document.template.css_template)

        # 4. Theme CSS custom properties
        theme = self._resolve_theme(document.theme)
        parts.append(self._get_theme_css(theme))

        return "\n".join(parts)

    def _get_font_css(self):
        """Generate @font-face declarations for self-hosted fonts."""
        fonts_base = f"{self.base_url}/static/fonts"
        return f"""
@font-face {{
  font-family: 'Inter';
  src: url('{fonts_base}/inter/Inter-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}}
@font-face {{
  font-family: 'Inter';
  src: url('{fonts_base}/inter/Inter-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
}}
@font-face {{
  font-family: 'Inter';
  src: url('{fonts_base}/inter/Inter-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
}}
@font-face {{
  font-family: 'Merriweather';
  src: url('{fonts_base}/merriweather/Merriweather-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}}
@font-face {{
  font-family: 'Merriweather';
  src: url('{fonts_base}/merriweather/Merriweather-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
}}
@font-face {{
  font-family: 'Source Sans Pro';
  src: url('{fonts_base}/source-sans-pro/SourceSansPro-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}}
@font-face {{
  font-family: 'Source Sans Pro';
  src: url('{fonts_base}/source-sans-pro/SourceSansPro-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
}}
"""

    def _get_print_css(self):
        """Return A4 print CSS with @page rules."""
        return f"""
@page {{
  size: A4 portrait;
  margin: {self.MARGIN_TOP_MM}mm {self.MARGIN_RIGHT_MM}mm {self.MARGIN_BOTTOM_MM}mm {self.MARGIN_LEFT_MM}mm;
}}

@page :first {{
  margin-top: {self.MARGIN_TOP_MM}mm;
}}

* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  padding: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

/* Page break controls */
.cv-section {{
  page-break-inside: avoid;
  break-inside: avoid;
}}

.cv-entry {{
  page-break-inside: avoid;
  break-inside: avoid;
}}

.cv-section__title {{
  page-break-after: avoid;
  break-after: avoid;
}}

/* Force page break where needed */
.page-break {{
  page-break-before: always;
  break-before: always;
}}

/* Hide elements not meant for print */
.no-print {{
  display: none !important;
}}

/* Ensure backgrounds print */
* {{
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
  color-adjust: exact !important;
}}
"""

    def _resolve_theme(self, theme_slug):
        """Resolve a theme slug to a dict of CSS custom property values."""
        THEMES = {
            "default": {
                "primary": "#2563eb",
                "secondary": "#64748b",
                "accent": "#f59e0b",
                "text": "#1e293b",
                "text_light": "#64748b",
                "background": "#ffffff",
                "surface": "#f8fafc",
                "border": "#e2e8f0",
                "sidebar_bg": "#1e293b",
                "sidebar_text": "#f1f5f9",
                "font_heading": "'Inter', sans-serif",
                "font_body": "'Source Sans Pro', sans-serif",
                "font_size_base": "10pt",
                "line_height": "1.5",
            },
            "professional-blue": {
                "primary": "#1e3a5f",
                "secondary": "#3b6ea5",
                "accent": "#d4a843",
                "text": "#1a1a2e",
                "text_light": "#6b7280",
                "background": "#ffffff",
                "surface": "#f0f4f8",
                "border": "#d1d9e6",
                "sidebar_bg": "#1e3a5f",
                "sidebar_text": "#f0f4f8",
                "font_heading": "'Merriweather', serif",
                "font_body": "'Source Sans Pro', sans-serif",
                "font_size_base": "10pt",
                "line_height": "1.5",
            },
            "elegant-dark": {
                "primary": "#2d3436",
                "secondary": "#636e72",
                "accent": "#e17055",
                "text": "#2d3436",
                "text_light": "#636e72",
                "background": "#ffffff",
                "surface": "#f5f5f5",
                "border": "#dfe6e9",
                "sidebar_bg": "#2d3436",
                "sidebar_text": "#dfe6e9",
                "font_heading": "'Inter', sans-serif",
                "font_body": "'Inter', sans-serif",
                "font_size_base": "10pt",
                "line_height": "1.5",
            },
            "modern-teal": {
                "primary": "#0d9488",
                "secondary": "#5eead4",
                "accent": "#f59e0b",
                "text": "#134e4a",
                "text_light": "#64748b",
                "background": "#ffffff",
                "surface": "#f0fdfa",
                "border": "#ccfbf1",
                "sidebar_bg": "#134e4a",
                "sidebar_text": "#f0fdfa",
                "font_heading": "'Inter', sans-serif",
                "font_body": "'Inter', sans-serif",
                "font_size_base": "10pt",
                "line_height": "1.5",
            },
        }
        return THEMES.get(theme_slug, THEMES["default"])

    def _get_theme_css(self, theme):
        """Generate CSS custom properties from theme dict."""
        props = "\n".join(
            f"  --cv-{key.replace('_', '-')}: {value};"
            for key, value in theme.items()
        )
        return f":root {{\n{props}\n}}"
```

---

## 2. Template / TemplateCategory / Theme Django Models

```python
# documents/models.py (template-related models)

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class TemplateCategory(models.Model):
    """
    Categories for template organization in the gallery.
    Allows filtering templates by use case.
    """

    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("URL-Kurzname"), max_length=50, unique=True)
    description = models.TextField(_("Beschreibung"), blank=True, default="")
    icon = models.CharField(
        _("Icon-CSS-Klasse"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("CSS-Klasse fuer ein Icon (z.B. Heroicons oder Lucide)"),
    )
    ordering = models.PositiveIntegerField(_("Reihenfolge"), default=0)

    class Meta:
        verbose_name = _("Vorlagen-Kategorie")
        verbose_name_plural = _("Vorlagen-Kategorien")
        db_table = "documents_templatecategory"
        ordering = ["ordering"]

    def __str__(self):
        return self.name


class Theme(models.Model):
    """
    Color/font theme that can be applied to any template.
    Stored as CSS custom property values.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("URL-Kurzname"), max_length=50, unique=True)

    # Color values (stored as hex strings)
    primary = models.CharField(_("Primärfarbe"), max_length=7, default="#2563eb")
    secondary = models.CharField(_("Sekundärfarbe"), max_length=7, default="#64748b")
    accent = models.CharField(_("Akzentfarbe"), max_length=7, default="#f59e0b")
    text_color = models.CharField(_("Textfarbe"), max_length=7, default="#1e293b")
    text_light = models.CharField(_("Helle Textfarbe"), max_length=7, default="#64748b")
    background = models.CharField(_("Hintergrund"), max_length=7, default="#ffffff")
    surface = models.CharField(_("Oberflächenfarbe"), max_length=7, default="#f8fafc")
    border = models.CharField(_("Rahmenfarbe"), max_length=7, default="#e2e8f0")
    sidebar_bg = models.CharField(
        _("Sidebar-Hintergrund"), max_length=7, default="#1e293b",
        help_text=_("Nur fuer Templates mit Sidebar"),
    )
    sidebar_text = models.CharField(
        _("Sidebar-Text"), max_length=7, default="#f1f5f9",
    )

    # Font settings
    font_heading = models.CharField(
        _("Schriftart Überschriften"), max_length=100,
        default="'Inter', sans-serif",
    )
    font_body = models.CharField(
        _("Schriftart Fliesstext"), max_length=100,
        default="'Source Sans Pro', sans-serif",
    )

    # Meta
    is_premium = models.BooleanField(_("Premium"), default=False)
    is_active = models.BooleanField(_("Aktiv"), default=True)
    ordering = models.PositiveIntegerField(_("Reihenfolge"), default=0)

    class Meta:
        verbose_name = _("Farbschema")
        verbose_name_plural = _("Farbschemata")
        db_table = "documents_theme"
        ordering = ["ordering"]

    def __str__(self):
        return self.name

    def to_css_dict(self):
        """Convert theme to dict for CSS custom property injection."""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "text": self.text_color,
            "text_light": self.text_light,
            "background": self.background,
            "surface": self.surface,
            "border": self.border,
            "sidebar_bg": self.sidebar_bg,
            "sidebar_text": self.sidebar_text,
            "font_heading": self.font_heading,
            "font_body": self.font_body,
        }

    @property
    def preview_swatch(self):
        """Return primary + secondary + accent for gallery display."""
        return [self.primary, self.secondary, self.accent]
```

---

## 3. Print CSS

```css
/* static/css/print.css — included in all PDF renders */

@page {
  size: A4 portrait;  /* 210mm x 297mm */
  margin: 15mm 20mm 15mm 20mm;
}

@page :first {
  margin-top: 15mm;
}

/* Reset for print */
*, *::before, *::after {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 210mm;
}

body {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
  color-adjust: exact;
}

/* Page break management */
.cv-section {
  page-break-inside: avoid;
  break-inside: avoid;
}

.cv-entry {
  page-break-inside: avoid;
  break-inside: avoid;
}

/* Keep section titles with their content */
.cv-section__title,
h2, h3 {
  page-break-after: avoid;
  break-after: avoid;
}

/* Force page break */
.page-break-before {
  page-break-before: always;
  break-before: always;
}

.page-break-after {
  page-break-after: always;
  break-after: always;
}

/* Avoid orphans and widows in text */
p {
  orphans: 3;
  widows: 3;
}

/* Hide elements not meant for PDF */
.no-print,
.editor-only,
.htmx-indicator,
button,
.btn {
  display: none !important;
}

/* Remove link styling for print */
a {
  color: inherit !important;
  text-decoration: none !important;
}

/* Ensure images respect boundaries */
img {
  max-width: 100%;
  height: auto;
}

/* Sidebar template: ensure full-height sidebar in print */
.cv-sidebar {
  min-height: 297mm;
  padding-bottom: 15mm;
}
```

---

## 4. Preview Rendering (HTML-Only for Editor)

```python
# editor/views.py (preview-related)

import hashlib
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache

from documents.models import Document
from documents.services import PDFRenderingService


class PreviewView(LoginRequiredMixin, View):
    """
    Render HTML preview for the editor iframe.
    No PDF generation — returns rendered HTML directly.
    Uses caching to avoid re-rendering unchanged content.
    """

    def get(self, request, document_id):
        document = Document.objects.get(
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        # Check cache
        cache_key = self._get_cache_key(document)
        cached_html = cache.get(cache_key)

        if cached_html:
            return HttpResponse(cached_html, content_type="text/html; charset=utf-8")

        # Render HTML (no PDF)
        service = PDFRenderingService()
        html = service.render_to_html(document)

        # Cache for 5 minutes (invalidated on content change)
        cache.set(cache_key, html, timeout=300)

        return HttpResponse(html, content_type="text/html; charset=utf-8")

    def _get_cache_key(self, document):
        """
        Generate a cache key based on document content + template + theme.
        Changes to any of these will produce a different key, effectively
        invalidating the cache.
        """
        import json
        # Collect all section content
        sections_hash = hashlib.md5()
        for section in document.sections.filter(is_visible=True).order_by("ordering"):
            sections_hash.update(
                json.dumps(section.content, sort_keys=True).encode()
            )
            sections_hash.update(str(section.ordering).encode())

        template_id = str(document.template_id) if document.template else "none"

        return (
            f"preview:{document.id}:{template_id}:{document.theme}"
            f":{sections_hash.hexdigest()}"
        )
```

---

## 5. PDF Caching Strategy

```python
# documents/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Document, Section


@receiver(post_save, sender=Section)
def invalidate_document_cache_on_section_change(sender, instance, **kwargs):
    """
    Invalidate PDF cache and preview cache when a section is updated.
    The actual PDF is only regenerated on explicit download request.
    """
    document = instance.document

    # Delete cached PDF file
    if document.pdf_file:
        document.pdf_file.delete(save=False)
        Document.objects.filter(id=document.id).update(pdf_file="")

    # Invalidate all preview cache entries for this document
    # (We use pattern-based invalidation since exact key depends on content)
    cache.delete_pattern(f"preview:{document.id}:*")


@receiver(post_save, sender=Document)
def invalidate_cache_on_document_change(sender, instance, update_fields=None, **kwargs):
    """
    Invalidate caches when document template or theme changes.
    """
    if update_fields and not {"template", "theme", "template_id"}.intersection(update_fields or set()):
        return  # Only invalidate on template/theme changes

    if instance.pdf_file:
        instance.pdf_file.delete(save=False)
        # Avoid recursive save by using update()
        Document.objects.filter(id=instance.id).update(pdf_file="")

    cache.delete_pattern(f"preview:{instance.id}:*")
```

### Caching Flow Summary

```
User edits section content
    → post_save signal fires on Section
    → Deletes document.pdf_file (cached PDF)
    → Invalidates preview cache keys
    → Next preview request: re-renders HTML (fast, ~50ms)
    → Next PDF download: re-renders PDF via WeasyPrint (~2-5s)

User changes template or theme
    → post_save signal fires on Document
    → Same invalidation flow

PDF download requested
    → Check if document.pdf_file exists
    → If yes: serve cached PDF immediately
    → If no: render via WeasyPrint, save to pdf_file, serve
```

---

## 6. Font Loading (Self-Hosted)

All fonts must be self-hosted due to the Landgericht Muenchen ruling prohibiting direct Google Fonts CDN usage (DSGVO violation, passing IP addresses to Google without consent).

### Directory Structure

```
static/
  fonts/
    inter/
      Inter-Regular.woff2
      Inter-SemiBold.woff2
      Inter-Bold.woff2
    merriweather/
      Merriweather-Regular.woff2
      Merriweather-Bold.woff2
    source-sans-pro/
      SourceSansPro-Regular.woff2
      SourceSansPro-SemiBold.woff2
    playfair/
      PlayfairDisplay-Bold.woff2
    fira-code/
      FiraCode-Regular.woff2
```

### Font Loading for WeasyPrint

WeasyPrint loads fonts from `@font-face` declarations in CSS. The `base_url` parameter in the HTML constructor tells WeasyPrint where to resolve relative URLs.

```python
# In PDFRenderingService.__init__:
self.base_url = getattr(settings, "WEASYPRINT_BASEURL", "http://web:8000")

# In production Docker: web service serves static files
# Alternatively, use absolute file paths:
fonts_path = Path(settings.STATIC_ROOT) / "fonts"
# and reference with file:// URLs in @font-face
```

### Font Management Command

```python
# documents/management/commands/download_fonts.py

import urllib.request
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


FONT_SOURCES = {
    "inter": {
        "Inter-Regular.woff2": "https://fonts.gstatic.com/s/inter/v13/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa2JL7W0Q5nw.woff2",
        "Inter-SemiBold.woff2": "https://fonts.gstatic.com/s/inter/v13/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa0pX7W0Q5nw.woff2",
        "Inter-Bold.woff2": "https://fonts.gstatic.com/s/inter/v13/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa25X7W0Q5nw.woff2",
    },
    # Add more font families as needed
}


class Command(BaseCommand):
    help = "Download and self-host web fonts (DSGVO compliance — LG Muenchen ruling)"

    def handle(self, *args, **options):
        fonts_dir = Path(settings.STATIC_ROOT) / "fonts"

        for family, files in FONT_SOURCES.items():
            family_dir = fonts_dir / family
            family_dir.mkdir(parents=True, exist_ok=True)

            for filename, url in files.items():
                filepath = family_dir / filename
                if filepath.exists():
                    self.stdout.write(f"  Already exists: {filepath}")
                    continue

                self.stdout.write(f"  Downloading: {filename}...")
                try:
                    urllib.request.urlretrieve(url, filepath)
                    self.stdout.write(self.style.SUCCESS(f"  Saved: {filepath}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  Failed: {e}"))

        self.stdout.write(self.style.SUCCESS("\nFont download complete."))
```

---

## 7. Document Download View

```python
# editor/views.py

from django.http import FileResponse, Http404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from documents.models import Document
from documents.services import PDFRenderingService


class DocumentDownloadView(LoginRequiredMixin, View):
    """
    Generate and serve PDF download.
    Uses cached PDF if available, otherwise renders fresh.
    Premium check: only premium users can download premium templates.
    """

    def get(self, request, document_id):
        try:
            document = Document.objects.get(
                id=document_id,
                user=request.user,
                deleted_at__isnull=True,
            )
        except Document.DoesNotExist:
            raise Http404

        # Premium check
        if document.is_premium and not request.user.profile.is_premium:
            from django.contrib import messages
            messages.warning(
                request,
                "Zum Herunterladen dieser Vorlage benötigen Sie ein Premium-Abonnement."
            )
            from django.shortcuts import redirect
            return redirect("payments:pricing")

        # Use cached PDF or render new one
        if document.pdf_file:
            pdf_file = document.pdf_file
        else:
            service = PDFRenderingService()
            service.render_and_save(document)
            document.refresh_from_db()
            pdf_file = document.pdf_file

        # Generate filename
        clean_title = document.title.replace(" ", "_")[:50]
        filename = f"{clean_title}.pdf"

        return FileResponse(
            pdf_file.open("rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )
```
