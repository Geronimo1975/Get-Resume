import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def _get_weasyprint():
    """Lazy import WeasyPrint to avoid requiring system libs at import time."""
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    return HTML, CSS, FontConfiguration


class PDFRenderingService:
    def __init__(self):
        self.font_config = None
        self.base_url = getattr(settings, "WEASYPRINT_BASEURL", "http://localhost:8000")

    def _ensure_font_config(self):
        if self.font_config is None:
            _, _, FontConfiguration = _get_weasyprint()
            self.font_config = FontConfiguration()

    def render_to_html(self, document):
        """Render document to full HTML string (for editor preview iframe)."""
        html_content = self._build_html(document)
        css_content = self._build_css(document)
        return f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><style>{self._get_font_css()}</style><style>{css_content}</style></head>
<body>{html_content}</body>
</html>"""

    def render_to_pdf(self, document):
        """Render document to PDF bytes via WeasyPrint."""
        html_content = self._build_html(document)
        css_content = self._build_css(document)
        full_html = f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><style>{self._get_font_css()}</style><style>{css_content}</style></head>
<body>{html_content}</body>
</html>"""
        HTML, CSS, _ = _get_weasyprint()
        self._ensure_font_config()
        html = HTML(string=full_html, base_url=self.base_url)
        css = CSS(string=self._get_print_css(), font_config=self.font_config)
        pdf_bytes = html.write_pdf(
            stylesheets=[css],
            font_config=self.font_config,
            presentational_hints=True,
        )
        logger.info(
            "PDF rendered for document %s (%d bytes)", document.id, len(pdf_bytes)
        )
        return pdf_bytes

    def render_and_save(self, document):
        """Render PDF and save to document.pdf_file."""
        if document.pdf_file:
            document.pdf_file.delete(save=False)
        pdf_bytes = self.render_to_pdf(document)
        filename = f"{document.id}.pdf"
        document.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
        return document.pdf_file

    def _build_html(self, document):
        """Build HTML from Django template + section data."""
        template = document.template
        slug = template.slug if template else "klassisch"
        template_path = f"cv/{slug}/lebenslauf.html"

        sections = document.sections.filter(is_visible=True).order_by("ordering")
        section_data = {}
        for section in sections:
            section_data[section.section_type] = section.content

        context = {
            "document": document,
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
            "fonts_base": f"{self.base_url}/static/fonts",
        }
        try:
            return render_to_string(template_path, context)
        except Exception:
            logger.exception(
                "Template rendering failed: %s, falling back to klassisch",
                template_path,
            )
            return render_to_string("cv/klassisch/lebenslauf.html", context)

    def _build_css(self, document):
        """Combine font + template + theme CSS."""
        parts = [self._get_font_css()]
        if document.template and document.template.css_template:
            parts.append(document.template.css_template)
        parts.append(self._get_theme_css(self._resolve_theme(document.theme)))
        return "\n".join(parts)

    def _get_font_css(self):
        fonts_base = f"{self.base_url}/static/fonts"
        return f"""
@font-face {{ font-family: 'Inter'; src: url('{fonts_base}/inter/Inter-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; }}
@font-face {{ font-family: 'Inter'; src: url('{fonts_base}/inter/Inter-SemiBold.woff2') format('woff2'); font-weight: 600; font-style: normal; }}
@font-face {{ font-family: 'Inter'; src: url('{fonts_base}/inter/Inter-Bold.woff2') format('woff2'); font-weight: 700; font-style: normal; }}
@font-face {{ font-family: 'Merriweather'; src: url('{fonts_base}/merriweather/Merriweather-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; }}
@font-face {{ font-family: 'Merriweather'; src: url('{fonts_base}/merriweather/Merriweather-Bold.woff2') format('woff2'); font-weight: 700; font-style: normal; }}
@font-face {{ font-family: 'Source Sans Pro'; src: url('{fonts_base}/source-sans-pro/SourceSansPro-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; }}
@font-face {{ font-family: 'Source Sans Pro'; src: url('{fonts_base}/source-sans-pro/SourceSansPro-SemiBold.woff2') format('woff2'); font-weight: 600; font-style: normal; }}
"""

    def _get_print_css(self):
        return """
@page { size: A4 portrait; margin: 15mm 20mm 15mm 20mm; }
@page :first { margin-top: 15mm; }
* { box-sizing: border-box; }
body { margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; color-adjust: exact; }
.cv-section { page-break-inside: avoid; break-inside: avoid; }
.cv-entry { page-break-inside: avoid; break-inside: avoid; }
.cv-section-title, h2, h3 { page-break-after: avoid; break-after: avoid; }
.page-break { page-break-before: always; break-before: always; }
p { orphans: 3; widows: 3; }
.no-print, button, .btn { display: none !important; }
a { color: inherit !important; text-decoration: none !important; }
img { max-width: 100%; height: auto; }
"""

    def _resolve_theme(self, theme_slug):
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
                "font_heading": "'Inter', sans-serif",
                "font_body": "'Source Sans Pro', sans-serif",
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
                "font_heading": "'Merriweather', serif",
                "font_body": "'Source Sans Pro', sans-serif",
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
                "font_heading": "'Inter', sans-serif",
                "font_body": "'Inter', sans-serif",
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
                "font_heading": "'Inter', sans-serif",
                "font_body": "'Inter', sans-serif",
            },
        }
        return THEMES.get(theme_slug, THEMES["default"])

    def _get_theme_css(self, theme):
        props = "\n".join(
            f"  --cv-{key.replace('_', '-')}: {value};"
            for key, value in theme.items()
        )
        return f":root {{\n{props}\n}}"
