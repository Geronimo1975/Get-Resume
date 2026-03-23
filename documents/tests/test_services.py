from django.test import SimpleTestCase
from documents.services import PDFRenderingService


class PDFRenderingServiceTest(SimpleTestCase):
    def test_resolve_theme_returns_default(self):
        service = PDFRenderingService()
        theme = service._resolve_theme("nonexistent")
        self.assertEqual(theme["primary"], "#2563eb")

    def test_resolve_theme_returns_named(self):
        service = PDFRenderingService()
        theme = service._resolve_theme("professional-blue")
        self.assertEqual(theme["primary"], "#1e3a5f")

    def test_get_theme_css_contains_custom_properties(self):
        service = PDFRenderingService()
        theme = service._resolve_theme("default")
        css = service._get_theme_css(theme)
        self.assertIn("--cv-primary", css)
        self.assertIn("#2563eb", css)

    def test_get_print_css_contains_a4(self):
        service = PDFRenderingService()
        css = service._get_print_css()
        self.assertIn("A4", css)

    def test_get_font_css_contains_inter(self):
        service = PDFRenderingService()
        css = service._get_font_css()
        self.assertIn("Inter", css)
        self.assertIn(".woff2", css)
