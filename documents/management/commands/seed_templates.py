from django.core.management.base import BaseCommand
from documents.models import Template

TEMPLATES = [
    {"name": "Klassisch", "slug": "klassisch", "category": "klassisch", "description": "Formaler, tabellarischer Lebenslauf. Ideal für Banken, Kanzleien, Behörden.", "is_premium": False, "ordering": 1},
    {"name": "Modern", "slug": "modern", "category": "modern", "description": "Seitenleiste mit Foto und Kontakt. Für Tech, Startups, Marketing.", "is_premium": False, "ordering": 2},
    {"name": "Kreativ", "slug": "kreativ", "category": "kreativ", "description": "Auffälliger Header mit Farbfläche. Für Design, Medien, Kreativbranche.", "is_premium": True, "ordering": 3},
]


class Command(BaseCommand):
    help = "Seed the 3 MVP CV templates"

    def handle(self, *args, **options):
        for data in TEMPLATES:
            obj, created = Template.objects.update_or_create(slug=data["slug"], defaults=data)
            self.stdout.write(f"  {'Created' if created else 'Updated'}: {obj.name}")
        self.stdout.write(self.style.SUCCESS("Template seeding complete."))
