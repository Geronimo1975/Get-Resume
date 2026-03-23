from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
)
from unfold.decorators import display

from .models import Document, Template, Section


class SectionInline(TabularInline):
    model = Section
    extra = 0
    fields = ("section_type", "title", "ordering", "is_visible")
    ordering = ("ordering",)


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ("title", "user", "display_doc_type", "template", "created_at", "display_deleted")
    list_filter = [
        ("doc_type", ChoicesDropdownFilter),
        "is_premium",
        ("created_at", RangeDateFilter),
        ("user", RelatedDropdownFilter),
    ]
    search_fields = ("title", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [SectionInline]

    compressed_fields = True
    warn_unsaved_form = True
    list_per_page = 25

    def get_queryset(self, request):
        """Show all documents including soft-deleted in admin."""
        return Document.all_objects.all()

    @display(
        description="Typ",
        label={
            "lebenslauf": "success",
            "anschreiben": "info",
            "deckblatt": "warning",
        },
    )
    def display_doc_type(self, obj):
        return obj.doc_type

    @display(
        description="Status",
        label={
            True: "danger",
            False: "success",
        },
    )
    def display_deleted(self, obj):
        return obj.is_deleted


@admin.register(Template)
class TemplateAdmin(ModelAdmin):
    list_display = ("name", "display_category", "display_premium", "display_active", "ordering")
    list_filter = [
        ("category", ChoicesDropdownFilter),
        "is_premium",
        "is_active",
    ]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("ordering",)

    compressed_fields = True
    list_per_page = 25

    @display(
        description="Kategorie",
        label={
            "klassisch": "info",
            "modern": "success",
            "kreativ": "warning",
            "akademisch": "info",
            "it_tech": "success",
            "student": "warning",
        },
    )
    def display_category(self, obj):
        return obj.category

    @display(
        description="Premium",
        label={
            True: "warning",
            False: "info",
        },
    )
    def display_premium(self, obj):
        return obj.is_premium

    @display(
        description="Aktiv",
        label={
            True: "success",
            False: "danger",
        },
    )
    def display_active(self, obj):
        return obj.is_active


@admin.register(Section)
class SectionAdmin(ModelAdmin):
    list_display = ("display_section_type", "document", "ordering", "display_visible")
    list_filter = [
        ("section_type", ChoicesDropdownFilter),
        "is_visible",
    ]

    list_per_page = 25

    @display(
        description="Abschnittstyp",
        label={
            "persoenliche_daten": "info",
            "berufserfahrung": "success",
            "ausbildung": "success",
            "kenntnisse": "warning",
            "sprachen": "warning",
            "weiterbildungen": "info",
            "ehrenamt": "info",
            "interessen": "info",
            "unterschrift": "info",
        },
    )
    def display_section_type(self, obj):
        return obj.section_type

    @display(
        description="Sichtbar",
        label={
            True: "success",
            False: "danger",
        },
    )
    def display_visible(self, obj):
        return obj.is_visible
