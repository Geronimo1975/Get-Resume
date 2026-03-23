# Editor Views Reference

Complete Django views for the HTMX-powered CV editor.

---

## URL Configuration

```python
# editor/urls.py

from django.urls import path
from . import views

app_name = "editor"

urlpatterns = [
    # Main editor page
    path(
        "lebenslauf-erstellen/",
        views.EditorCreateView.as_view(),
        name="editor_create",
    ),
    path(
        "lebenslauf-bearbeiten/<uuid:document_id>/",
        views.EditorView.as_view(),
        name="editor",
    ),

    # Section CRUD (HTMX endpoints)
    path(
        "api/editor/<uuid:document_id>/sections/",
        views.SectionCreateView.as_view(),
        name="section_create",
    ),
    path(
        "api/editor/sections/<uuid:section_id>/",
        views.SectionUpdateView.as_view(),
        name="section_update",
    ),
    path(
        "api/editor/sections/<uuid:section_id>/delete/",
        views.SectionDeleteView.as_view(),
        name="section_delete",
    ),
    path(
        "api/editor/<uuid:document_id>/sections/reorder/",
        views.SectionReorderView.as_view(),
        name="section_reorder",
    ),

    # Preview
    path(
        "api/editor/<uuid:document_id>/preview/",
        views.PreviewView.as_view(),
        name="preview",
    ),

    # Photo upload
    path(
        "api/editor/<uuid:document_id>/photo/",
        views.PhotoUploadView.as_view(),
        name="photo_upload",
    ),

    # Template switching
    path(
        "api/editor/<uuid:document_id>/template/",
        views.TemplateSelectView.as_view(),
        name="template_select",
    ),

    # PDF download
    path(
        "api/editor/<uuid:document_id>/download/",
        views.DocumentDownloadView.as_view(),
        name="document_download",
    ),

    # Template gallery (public page)
    path(
        "vorlagen/",
        views.TemplateGalleryView.as_view(),
        name="template_gallery",
    ),
]
```

---

## 1. EditorView (Main Editor Page)

```python
# editor/views.py

import uuid
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone

from documents.models import Document, Template, Section

logger = logging.getLogger(__name__)


class EditorCreateView(LoginRequiredMixin, View):
    """
    Create a new document and redirect to the editor.
    If user has hit free plan limit, redirect to pricing.
    """

    def get(self, request):
        user = request.user

        # Check document limit for free users
        if not user.profile.is_premium:
            doc_count = Document.objects.filter(
                user=user, deleted_at__isnull=True
            ).count()
            if doc_count >= 1:  # Free: max 1 document
                messages.warning(
                    request,
                    "Im kostenlosen Plan können Sie nur einen Lebenslauf erstellen. "
                    "Upgraden Sie auf Premium für unbegrenzte Dokumente."
                )
                return redirect("payments:pricing")

        # Create new document with default template
        default_template = Template.objects.filter(
            is_active=True, category="klassisch"
        ).first()

        document = Document.objects.create(
            user=user,
            doc_type=Document.DocType.LEBENSLAUF,
            title="Mein Lebenslauf",
            template=default_template,
            theme="default",
        )

        # Create default sections
        default_sections = [
            ("persoenliche_daten", 0),
            ("berufserfahrung", 1),
            ("ausbildung", 2),
            ("kenntnisse", 3),
            ("sprachen", 4),
            ("unterschrift", 5),
        ]
        for section_type, ordering in default_sections:
            Section.objects.create(
                document=document,
                section_type=section_type,
                ordering=ordering,
                content={},
            )

        return redirect("editor:editor", document_id=document.id)


class EditorView(LoginRequiredMixin, View):
    """
    Main editor page. Loads the full editor layout with:
    - Sidebar with section list
    - Center form area
    - Right preview iframe
    """

    def get(self, request, document_id):
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        sections = document.sections.order_by("ordering")
        templates = Template.objects.filter(is_active=True).order_by("ordering")

        # Determine which section to show in the form
        active_section_id = request.GET.get("section")
        if active_section_id:
            active_section = sections.filter(id=active_section_id).first()
        else:
            active_section = sections.first()

        # Available section types (for "Add Section" dropdown)
        existing_types = set(sections.values_list("section_type", flat=True))
        available_types = [
            (value, label)
            for value, label in Section.SectionType.choices
            if value not in existing_types
        ]

        context = {
            "document": document,
            "sections": sections,
            "active_section": active_section,
            "templates": templates,
            "available_section_types": available_types,
            "is_premium": request.user.profile.is_premium,
        }

        return render(request, "editor/editor_base.html", context)
```

---

## 2. SectionCreateView

```python
class SectionCreateView(LoginRequiredMixin, View):
    """
    Create a new section for a document.
    Called via hx-post from the "Add Section" button.
    Returns the new section form partial.
    """

    def post(self, request, document_id):
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        section_type = request.POST.get("section_type", "")

        # Validate section type
        valid_types = [choice[0] for choice in Section.SectionType.choices]
        if section_type not in valid_types:
            return HttpResponse(
                '<div class="text-red-600 text-sm p-2">'
                'Ungültiger Abschnittstyp.</div>',
                status=400,
            )

        # Check for duplicate section type
        if document.sections.filter(section_type=section_type).exists():
            return HttpResponse(
                '<div class="text-red-600 text-sm p-2">'
                'Dieser Abschnitt existiert bereits.</div>',
                status=400,
            )

        # Determine ordering (add at end)
        max_ordering = document.sections.aggregate(
            max_ord=models.Max("ordering")
        )["max_ord"] or 0

        section = Section.objects.create(
            document=document,
            section_type=section_type,
            ordering=max_ordering + 1,
            content={},
        )

        # Return the sidebar item + section form partial
        if request.htmx:
            return render(request, "editor/partials/section_sidebar_item.html", {
                "section": section,
                "active": True,
                "document": document,
            })

        return redirect("editor:editor", document_id=document.id)
```

---

## 3. SectionUpdateView (Autosave)

```python
class SectionUpdateView(LoginRequiredMixin, View):
    """
    Update a section's content.
    Called via hx-put with debounced autosave (500ms).
    Returns hx-swap="none" — no DOM update needed, just save.
    """

    def put(self, request, section_id):
        from django.http import QueryDict
        put_data = QueryDict(request.body)

        section = get_object_or_404(
            Section,
            id=section_id,
            document__user=request.user,
            document__deleted_at__isnull=True,
        )

        # Parse content from form data
        content = self._parse_form_data(section.section_type, put_data)

        # Update section
        section.content = content
        section.save(update_fields=["content", "updated_at"])

        # Return minimal response (autosave, no DOM swap)
        response = HttpResponse(status=204)
        # HTMX: trigger preview refresh
        response["HX-Trigger"] = "preview-refresh"
        return response

    def _parse_form_data(self, section_type, data):
        """
        Parse flat form data into structured JSON content.
        Handles repeatable entries (Berufserfahrung, Ausbildung, etc.)
        """
        if section_type == "persoenliche_daten":
            return {
                "vorname": data.get("vorname", ""),
                "nachname": data.get("nachname", ""),
                "anrede": data.get("anrede", ""),
                "geburtsdatum": data.get("geburtsdatum", ""),
                "geburtsort": data.get("geburtsort", ""),
                "staatsangehoerigkeit": data.get("staatsangehoerigkeit", ""),
                "familienstand": data.get("familienstand", ""),
                "email": data.get("email", ""),
                "telefon": data.get("telefon", ""),
                "strasse": data.get("strasse", ""),
                "plz": data.get("plz", ""),
                "stadt": data.get("stadt", ""),
                "website": data.get("website", ""),
                "linkedin": data.get("linkedin", ""),
                "xing": data.get("xing", ""),
                "foto": data.get("foto", ""),
            }

        elif section_type in ("berufserfahrung", "ausbildung", "ehrenamt", "weiterbildungen"):
            return self._parse_repeatable_entries(data)

        elif section_type == "kenntnisse":
            return self._parse_skill_entries(data)

        elif section_type == "sprachen":
            return self._parse_language_entries(data)

        elif section_type == "interessen":
            # Comma-separated tags
            tags_str = data.get("interessen", "")
            return {
                "eintraege": [t.strip() for t in tags_str.split(",") if t.strip()]
            }

        elif section_type == "unterschrift":
            return {
                "ort": data.get("ort", ""),
                "datum": data.get("datum", ""),
            }

        return {}

    def _parse_repeatable_entries(self, data):
        """Parse repeatable form entries (entries with index: entry_0_position, entry_1_position, etc.)."""
        entries = []
        index = 0
        while True:
            prefix = f"entry_{index}_"
            # Check if this entry index exists
            if not any(key.startswith(prefix) for key in data.keys()):
                break

            entry = {}
            for key, value in data.items():
                if key.startswith(prefix):
                    field_name = key[len(prefix):]
                    entry[field_name] = value

            # Handle list fields (aufgaben)
            aufgaben_str = entry.pop("aufgaben", "")
            if aufgaben_str:
                entry["aufgaben"] = [
                    a.strip() for a in aufgaben_str.split("\n") if a.strip()
                ]

            # Handle boolean
            entry["ist_aktuell"] = entry.get("ist_aktuell") in ("on", "true", "True")

            if not entry.get("id"):
                entry["id"] = str(uuid.uuid4())

            entries.append(entry)
            index += 1

        return {"eintraege": entries}

    def _parse_skill_entries(self, data):
        """Parse skill entries with rating."""
        entries = []
        index = 0
        while True:
            name = data.get(f"skill_{index}_name")
            if name is None:
                break
            entries.append({
                "id": data.get(f"skill_{index}_id", str(uuid.uuid4())),
                "name": name,
                "kategorie": data.get(f"skill_{index}_kategorie", ""),
                "niveau": int(data.get(f"skill_{index}_niveau", 3)),
            })
            index += 1
        return {"eintraege": entries}

    def _parse_language_entries(self, data):
        """Parse language entries with CEFR levels."""
        entries = []
        index = 0
        while True:
            sprache = data.get(f"lang_{index}_sprache")
            if sprache is None:
                break
            entries.append({
                "id": data.get(f"lang_{index}_id", str(uuid.uuid4())),
                "sprache": sprache,
                "niveau": data.get(f"lang_{index}_niveau", "B1"),
                "ist_muttersprache": data.get(f"lang_{index}_muttersprache") in ("on", "true"),
            })
            index += 1
        return {"eintraege": entries}
```

---

## 4. SectionDeleteView

```python
class SectionDeleteView(LoginRequiredMixin, View):
    """
    Delete a section.
    Called via hx-delete with a confirmation step.
    """

    def delete(self, request, section_id):
        section = get_object_or_404(
            Section,
            id=section_id,
            document__user=request.user,
            document__deleted_at__isnull=True,
        )

        # Prevent deleting required sections
        required_types = ["persoenliche_daten"]
        if section.section_type in required_types:
            return HttpResponse(
                '<div class="text-red-600 text-sm p-2">'
                'Persönliche Daten können nicht gelöscht werden.</div>',
                status=400,
            )

        document = section.document
        section.delete()

        # Re-number remaining sections
        for i, s in enumerate(document.sections.order_by("ordering")):
            if s.ordering != i:
                s.ordering = i
                s.save(update_fields=["ordering"])

        # Return empty string to remove the element from DOM
        response = HttpResponse("")
        response["HX-Trigger"] = "preview-refresh, sidebar-refresh"
        return response
```

---

## 5. SectionReorderView

```python
class SectionReorderView(LoginRequiredMixin, View):
    """
    Reorder sections based on drag & drop.
    Receives ordered list of section IDs from Sortable.js.
    """

    def post(self, request, document_id):
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        import json
        try:
            body = json.loads(request.body)
            section_ids = body.get("section_ids", [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Validate all IDs belong to this document
        sections = {
            str(s.id): s
            for s in document.sections.all()
        }

        for ordering, section_id in enumerate(section_ids):
            if section_id not in sections:
                continue
            section = sections[section_id]
            if section.ordering != ordering:
                section.ordering = ordering
                section.save(update_fields=["ordering"])

        response = HttpResponse(status=204)
        response["HX-Trigger"] = "preview-refresh"
        return response
```

---

## 6. PreviewView

```python
class PreviewView(LoginRequiredMixin, View):
    """
    Render HTML preview for the editor iframe.
    Called on every content change via hx-trigger="preview-refresh".
    Optionally accepts ?template=slug for template switching preview.
    """

    def get(self, request, document_id):
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        # Optional template override for preview
        template_slug = request.GET.get("template")
        if template_slug:
            preview_template = Template.objects.filter(
                slug=template_slug, is_active=True
            ).first()
            if preview_template:
                # Temporarily override template for preview only
                document.template = preview_template

        from documents.services import PDFRenderingService
        service = PDFRenderingService()
        html = service.render_to_html(document)

        return HttpResponse(html, content_type="text/html; charset=utf-8")
```

---

## 7. PhotoUploadView

```python
class PhotoUploadView(LoginRequiredMixin, View):
    """
    Upload, crop, and resize a profile photo.
    Accepts multipart POST with image file.
    Processes with Pillow: resize to max 600x800, optimize JPEG.
    """

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    OUTPUT_MAX_WIDTH = 600
    OUTPUT_MAX_HEIGHT = 800
    OUTPUT_QUALITY = 85

    def post(self, request, document_id):
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        photo = request.FILES.get("photo")
        if not photo:
            return HttpResponse(
                '<div class="text-red-600">Kein Foto ausgewählt.</div>',
                status=400,
            )

        # Validate file size
        if photo.size > self.MAX_FILE_SIZE:
            return HttpResponse(
                '<div class="text-red-600">Datei zu groß (max. 5 MB).</div>',
                status=400,
            )

        # Validate content type
        if photo.content_type not in self.ALLOWED_TYPES:
            return HttpResponse(
                '<div class="text-red-600">Nur JPEG, PNG und WebP sind erlaubt.</div>',
                status=400,
            )

        # Process image with Pillow
        from PIL import Image
        import io
        from django.core.files.base import ContentFile

        try:
            img = Image.open(photo)

            # Convert to RGB if necessary (e.g., PNG with alpha)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Apply crop data if provided (from Cropper.js)
            crop_x = int(request.POST.get("crop_x", 0))
            crop_y = int(request.POST.get("crop_y", 0))
            crop_width = int(request.POST.get("crop_width", 0))
            crop_height = int(request.POST.get("crop_height", 0))

            if crop_width > 0 and crop_height > 0:
                img = img.crop((
                    crop_x,
                    crop_y,
                    crop_x + crop_width,
                    crop_y + crop_height,
                ))

            # Resize maintaining aspect ratio
            img.thumbnail(
                (self.OUTPUT_MAX_WIDTH, self.OUTPUT_MAX_HEIGHT),
                Image.Resampling.LANCZOS,
            )

            # Strip EXIF data (privacy / DSGVO)
            # PIL strips EXIF on save unless explicitly kept

            # Save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=self.OUTPUT_QUALITY, optimize=True)
            buffer.seek(0)

            # Save file
            filename = f"photos/{document.user.id}/{document.id}_photo.jpg"
            from django.core.files.storage import default_storage

            # Delete old photo if exists
            persoenliche = document.sections.filter(
                section_type="persoenliche_daten"
            ).first()
            if persoenliche and persoenliche.content.get("foto"):
                old_path = persoenliche.content["foto"]
                if default_storage.exists(old_path):
                    default_storage.delete(old_path)

            # Save new photo
            saved_path = default_storage.save(
                filename,
                ContentFile(buffer.read()),
            )

            # Update section content
            if persoenliche:
                persoenliche.content["foto"] = saved_path
                persoenliche.save(update_fields=["content", "updated_at"])

            # Return updated photo preview partial
            return render(request, "editor/partials/photo_preview.html", {
                "photo_url": default_storage.url(saved_path),
                "document": document,
            })

        except Exception:
            logger.exception("Photo processing failed for document %s", document_id)
            return HttpResponse(
                '<div class="text-red-600">'
                'Fehler beim Verarbeiten des Fotos. Bitte versuchen Sie es erneut.'
                '</div>',
                status=500,
            )
```

---

## 8. TemplateSelectView

```python
class TemplateSelectView(LoginRequiredMixin, View):
    """
    Switch the document's template.
    GET: Show template gallery modal/panel
    POST: Apply selected template
    """

    def get(self, request, document_id):
        """Show template selection panel."""
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
        )

        templates = Template.objects.filter(is_active=True).order_by("ordering")
        categories = Template.Category.choices
        is_premium = request.user.profile.is_premium

        return render(request, "editor/partials/template_selector.html", {
            "document": document,
            "templates": templates,
            "categories": categories,
            "current_template": document.template,
            "is_premium": is_premium,
        })

    def post(self, request, document_id):
        """Apply selected template to document."""
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        template_slug = request.POST.get("template_slug", "")
        template = get_object_or_404(Template, slug=template_slug, is_active=True)

        # Premium check
        if template.is_premium and not request.user.profile.is_premium:
            return HttpResponse(
                '<div class="text-amber-600 text-sm p-2">'
                'Diese Vorlage erfordert ein Premium-Abonnement.'
                '</div>',
                status=403,
            )

        # Update document template
        document.template = template
        document.save(update_fields=["template", "updated_at"])

        # Mark as premium if template is premium
        if template.is_premium and not document.is_premium:
            document.is_premium = True
            document.save(update_fields=["is_premium"])

        # Return response with preview refresh trigger
        response = HttpResponse(
            '<div class="text-green-600 text-sm p-2">'
            f'Vorlage "{template.name}" wurde angewendet.'
            '</div>'
        )
        response["HX-Trigger"] = "preview-refresh, template-changed"
        return response
```

---

## 9. DocumentDownloadView

```python
class DocumentDownloadView(LoginRequiredMixin, View):
    """
    Generate and serve PDF download.
    Uses cached PDF if available, otherwise renders with WeasyPrint.
    """

    def get(self, request, document_id):
        document = get_object_or_404(
            Document,
            id=document_id,
            user=request.user,
            deleted_at__isnull=True,
        )

        # Premium check
        if document.is_premium and not request.user.profile.is_premium:
            messages.warning(
                request,
                "Zum Herunterladen dieser Vorlage benötigen Sie ein Premium-Abonnement."
            )
            return redirect("payments:pricing")

        # Check for cached PDF
        if document.pdf_file:
            return self._serve_pdf(document)

        # Render fresh PDF
        from documents.services import PDFRenderingService
        service = PDFRenderingService()

        try:
            service.render_and_save(document)
            document.refresh_from_db()
            return self._serve_pdf(document)

        except Exception:
            logger.exception("PDF generation failed for document %s", document_id)
            messages.error(
                request,
                "PDF konnte nicht erstellt werden. Bitte versuchen Sie es erneut."
            )
            return redirect("editor:editor", document_id=document_id)

    def _serve_pdf(self, document):
        """Serve the PDF file as download."""
        from django.http import FileResponse

        clean_title = "".join(
            c for c in document.title if c.isalnum() or c in (" ", "-", "_")
        ).strip()[:50] or "Lebenslauf"
        filename = f"{clean_title}.pdf"

        return FileResponse(
            document.pdf_file.open("rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )
```

---

## 10. Template Gallery View (Public)

```python
class TemplateGalleryView(TemplateView):
    """
    Public template gallery page at /vorlagen/.
    Shows all templates organized by category.
    Unauthenticated users see a CTA to sign up.
    """

    template_name = "editor/template_gallery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        templates = Template.objects.filter(is_active=True).order_by("ordering")
        categories = []

        for value, label in Template.Category.choices:
            cat_templates = templates.filter(category=value)
            if cat_templates.exists():
                categories.append({
                    "value": value,
                    "label": label,
                    "templates": cat_templates,
                })

        context["categories"] = categories
        context["total_count"] = templates.count()

        if self.request.user.is_authenticated:
            context["is_premium"] = self.request.user.profile.is_premium
        else:
            context["is_premium"] = False

        return context
```

---

## Helper: Section Form Routing

```python
# editor/views.py (continued)

class SectionFormView(LoginRequiredMixin, View):
    """
    Load the appropriate form partial for a section type.
    Called when clicking a section in the sidebar.
    """

    def get(self, request, section_id):
        section = get_object_or_404(
            Section,
            id=section_id,
            document__user=request.user,
        )

        # Map section types to form templates
        template_map = {
            "persoenliche_daten": "editor/forms/persoenliche_daten.html",
            "berufserfahrung": "editor/forms/berufserfahrung.html",
            "ausbildung": "editor/forms/ausbildung.html",
            "kenntnisse": "editor/forms/kenntnisse.html",
            "sprachen": "editor/forms/sprachen.html",
            "weiterbildungen": "editor/forms/weiterbildungen.html",
            "ehrenamt": "editor/forms/ehrenamt.html",
            "interessen": "editor/forms/interessen.html",
            "unterschrift": "editor/forms/unterschrift.html",
        }

        template_name = template_map.get(
            section.section_type,
            "editor/forms/generic.html",
        )

        return render(request, template_name, {
            "section": section,
            "content": section.content,
            "document": section.document,
        })
```
