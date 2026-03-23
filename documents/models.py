import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Manager that includes soft-deleted records (for admin/DSGVO audit)."""
    pass


class Document(models.Model):
    """
    Core document model for Lebenslauf, Bewerbungsschreiben, and Deckblatt.
    Content stored as JSON for flexible schema (sections can vary by template).
    Soft delete via deleted_at for DSGVO audit trail.
    """

    class DocType(models.TextChoices):
        LEBENSLAUF = "lebenslauf", _("Lebenslauf")
        ANSCHREIBEN = "anschreiben", _("Bewerbungsschreiben")
        DECKBLATT = "deckblatt", _("Deckblatt")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Benutzer"),
    )
    doc_type = models.CharField(
        _("Dokumenttyp"),
        max_length=20,
        choices=DocType.choices,
        default=DocType.LEBENSLAUF,
    )
    title = models.CharField(
        _("Titel"),
        max_length=255,
        default="Mein Lebenslauf",
        help_text=_("Interner Titel zur Unterscheidung Ihrer Dokumente"),
    )
    content = models.JSONField(
        _("Inhalt"),
        default=dict,
        blank=True,
        help_text=_("Strukturierter Inhalt des Dokuments als JSON"),
    )
    template = models.ForeignKey(
        "Template",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        verbose_name=_("Vorlage"),
    )
    theme = models.CharField(
        _("Farbschema"),
        max_length=50,
        default="default",
        help_text=_("CSS-Farbschema fuer die Vorlage"),
    )
    is_premium = models.BooleanField(
        _("Premium-Dokument"),
        default=False,
        help_text=_("Erfordert Premium-Abonnement zum Herunterladen"),
    )
    pdf_file = models.FileField(
        _("PDF-Datei"),
        upload_to="documents/pdfs/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Gecachte PDF-Version des Dokuments"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)
    deleted_at = models.DateTimeField(
        _("Gelöscht am"),
        null=True,
        blank=True,
        help_text=_("Soft-Delete Zeitstempel (DSGVO-konform)"),
    )

    # Managers
    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        verbose_name = _("Dokument")
        verbose_name_plural = _("Dokumente")
        db_table = "documents_document"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"], name="idx_doc_user_updated"),
            models.Index(fields=["doc_type"], name="idx_doc_type"),
            models.Index(fields=["deleted_at"], name="idx_doc_deleted"),
            models.Index(fields=["created_at"], name="idx_doc_created"),
        ]

    def __str__(self):
        return f"{self.get_doc_type_display()}: {self.title}"

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        """Mark document as deleted without removing from database."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        """Restore a soft-deleted document."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def invalidate_pdf_cache(self):
        """Delete cached PDF when content or style changes."""
        if self.pdf_file:
            self.pdf_file.delete(save=False)
            self.pdf_file = None
            self.save(update_fields=["pdf_file"])


class Template(models.Model):
    """
    CV/document template definition.
    Contains HTML template structure and associated CSS styling.
    """

    class Category(models.TextChoices):
        KLASSISCH = "klassisch", _("Klassisch")
        MODERN = "modern", _("Modern")
        KREATIV = "kreativ", _("Kreativ")
        AKADEMISCH = "akademisch", _("Akademisch")
        IT_TECH = "it_tech", _("IT & Technik")
        STUDENT = "student", _("Student / Berufseinsteiger")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        _("Name"),
        max_length=100,
        help_text=_("Anzeigename der Vorlage"),
    )
    slug = models.SlugField(
        _("URL-Kurzname"),
        max_length=100,
        unique=True,
        help_text=_("URL-freundlicher Name (z.B. 'klassisch-blau')"),
    )
    category = models.CharField(
        _("Kategorie"),
        max_length=20,
        choices=Category.choices,
        default=Category.KLASSISCH,
    )
    description = models.TextField(
        _("Beschreibung"),
        blank=True,
        default="",
        help_text=_("Kurzbeschreibung fuer die Vorlagen-Galerie"),
    )
    html_template = models.TextField(
        _("HTML-Vorlage"),
        help_text=_("Django-Template-Code fuer die Lebenslauf-Struktur"),
    )
    css_template = models.TextField(
        _("CSS-Stile"),
        help_text=_("CSS-Code fuer das Layout und Design"),
    )
    thumbnail = models.ImageField(
        _("Vorschaubild"),
        upload_to="templates/thumbnails/",
        blank=True,
        null=True,
        help_text=_("Vorschaubild fuer die Galerie (300x424px empfohlen)"),
    )
    is_premium = models.BooleanField(
        _("Premium-Vorlage"),
        default=False,
        help_text=_("Nur fuer Premium-Abonnenten verfuegbar"),
    )
    is_active = models.BooleanField(
        _("Aktiv"),
        default=True,
    )
    ordering = models.PositiveIntegerField(
        _("Reihenfolge"),
        default=0,
        help_text=_("Anzeigereihenfolge in der Galerie (kleiner = weiter vorn)"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        verbose_name = _("Vorlage")
        verbose_name_plural = _("Vorlagen")
        db_table = "documents_template"
        ordering = ["ordering", "name"]
        indexes = [
            models.Index(fields=["category", "ordering"], name="idx_template_cat_order"),
            models.Index(fields=["slug"], name="idx_template_slug"),
            models.Index(fields=["is_premium", "is_active"], name="idx_template_premium"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Section(models.Model):
    """
    Individual section within a document.
    Sections are ordered and can be toggled visible/invisible.
    Content stored as JSON for flexibility.
    """

    class SectionType(models.TextChoices):
        PERSOENLICHE_DATEN = "persoenliche_daten", _("Persönliche Daten")
        BERUFSERFAHRUNG = "berufserfahrung", _("Berufserfahrung")
        AUSBILDUNG = "ausbildung", _("Ausbildung")
        KENNTNISSE = "kenntnisse", _("Kenntnisse")
        SPRACHEN = "sprachen", _("Sprachen")
        WEITERBILDUNGEN = "weiterbildungen", _("Weiterbildungen")
        EHRENAMT = "ehrenamt", _("Ehrenamt")
        INTERESSEN = "interessen", _("Interessen")
        UNTERSCHRIFT = "unterschrift", _("Unterschrift")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("Dokument"),
    )
    section_type = models.CharField(
        _("Abschnittstyp"),
        max_length=30,
        choices=SectionType.choices,
    )
    title = models.CharField(
        _("Abschnittstitel"),
        max_length=100,
        blank=True,
        default="",
        help_text=_("Optionaler benutzerdefinierter Titel"),
    )
    content = models.JSONField(
        _("Inhalt"),
        default=dict,
        blank=True,
        help_text=_("Strukturierter Inhalt des Abschnitts als JSON"),
    )
    ordering = models.PositiveIntegerField(
        _("Reihenfolge"),
        default=0,
    )
    is_visible = models.BooleanField(
        _("Sichtbar"),
        default=True,
        help_text=_("Abschnitt im Dokument anzeigen"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        verbose_name = _("Abschnitt")
        verbose_name_plural = _("Abschnitte")
        db_table = "documents_section"
        ordering = ["ordering"]
        indexes = [
            models.Index(
                fields=["document", "ordering"],
                name="idx_section_doc_order",
            ),
            models.Index(
                fields=["section_type"],
                name="idx_section_type",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "section_type"],
                name="unique_section_per_document",
            ),
        ]

    def __str__(self):
        return f"{self.get_section_type_display()} (#{self.ordering})"

    def get_default_title(self):
        """Return the German default title for this section type."""
        defaults = {
            self.SectionType.PERSOENLICHE_DATEN: "Persönliche Daten",
            self.SectionType.BERUFSERFAHRUNG: "Berufserfahrung",
            self.SectionType.AUSBILDUNG: "Ausbildung",
            self.SectionType.KENNTNISSE: "Kenntnisse",
            self.SectionType.SPRACHEN: "Sprachen",
            self.SectionType.WEITERBILDUNGEN: "Weiterbildungen",
            self.SectionType.EHRENAMT: "Ehrenamt",
            self.SectionType.INTERESSEN: "Interessen",
            self.SectionType.UNTERSCHRIFT: "Unterschrift",
        }
        return defaults.get(self.section_type, self.section_type)
