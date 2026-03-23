# Django Models Reference

Complete model definitions for all apps in the Lebenslauf-Builder SaaS platform.

## accounts app

### Custom User Model

```python
# accounts/models.py

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Die E-Mail-Adresse muss angegeben werden."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser muss is_staff=True haben."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser muss is_superuser=True haben."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model using email instead of username.
    UUID primary key for all user-facing URLs and API endpoints.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )
    username = None  # Remove username field
    email = models.EmailField(
        _("E-Mail-Adresse"),
        unique=True,
        error_messages={
            "unique": _("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits."),
        },
    )
    first_name = models.CharField(_("Vorname"), max_length=150)
    last_name = models.CharField(_("Nachname"), max_length=150)
    is_email_verified = models.BooleanField(
        _("E-Mail bestätigt"),
        default=False,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Benutzer")
        verbose_name_plural = _("Benutzer")
        db_table = "accounts_user"
        indexes = [
            models.Index(fields=["email"], name="idx_user_email"),
            models.Index(fields=["date_joined"], name="idx_user_joined"),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def has_active_subscription(self):
        """Check if user has an active premium subscription."""
        return hasattr(self, "subscription") and self.subscription.is_active
```

### UserProfile Model

```python
class UserProfile(models.Model):
    """
    Extended user profile with German-specific fields and DSGVO consent tracking.
    Created automatically via post_save signal when User is created.
    """

    class Anrede(models.TextChoices):
        HERR = "herr", _("Herr")
        FRAU = "frau", _("Frau")
        DIVERS = "divers", _("Divers")
        KEINE = "keine", _("Keine Angabe")

    class SubscriptionPlan(models.TextChoices):
        FREE = "free", _("Kostenlos")
        PREMIUM_MONTHLY = "premium_monthly", _("Premium Monatlich")
        PREMIUM_YEARLY = "premium_yearly", _("Premium Jährlich")
        BUSINESS = "business", _("Business")

    class Language(models.TextChoices):
        DE = "de", _("Deutsch")
        EN = "en", _("English")

    class Bundesland(models.TextChoices):
        BW = "BW", _("Baden-Württemberg")
        BY = "BY", _("Bayern")
        BE = "BE", _("Berlin")
        BB = "BB", _("Brandenburg")
        HB = "HB", _("Bremen")
        HH = "HH", _("Hamburg")
        HE = "HE", _("Hessen")
        MV = "MV", _("Mecklenburg-Vorpommern")
        NI = "NI", _("Niedersachsen")
        NW = "NW", _("Nordrhein-Westfalen")
        RP = "RP", _("Rheinland-Pfalz")
        SL = "SL", _("Saarland")
        SN = "SN", _("Sachsen")
        ST = "ST", _("Sachsen-Anhalt")
        SH = "SH", _("Schleswig-Holstein")
        TH = "TH", _("Thüringen")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Benutzer"),
    )

    # Personal information
    anrede = models.CharField(
        _("Anrede"),
        max_length=10,
        choices=Anrede.choices,
        default=Anrede.KEINE,
    )
    geburtsdatum = models.DateField(
        _("Geburtsdatum"),
        null=True,
        blank=True,
    )
    telefon = models.CharField(
        _("Telefonnummer"),
        max_length=30,
        blank=True,
        default="",
    )

    # Address
    strasse = models.CharField(
        _("Straße und Hausnummer"),
        max_length=255,
        blank=True,
        default="",
    )
    plz = models.CharField(
        _("Postleitzahl"),
        max_length=10,
        blank=True,
        default="",
    )
    stadt = models.CharField(
        _("Stadt"),
        max_length=100,
        blank=True,
        default="",
    )
    bundesland = models.CharField(
        _("Bundesland"),
        max_length=2,
        choices=Bundesland.choices,
        blank=True,
        default="",
    )

    # Subscription
    subscription_plan = models.CharField(
        _("Abonnement"),
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
    )
    subscription_expires_at = models.DateTimeField(
        _("Abonnement läuft ab am"),
        null=True,
        blank=True,
    )

    # Preferences
    preferred_language = models.CharField(
        _("Bevorzugte Sprache"),
        max_length=2,
        choices=Language.choices,
        default=Language.DE,
    )

    # DSGVO / Privacy fields
    privacy_accepted_at = models.DateTimeField(
        _("Datenschutzerklaerung akzeptiert am"),
        null=True,
        blank=True,
        help_text=_("Zeitpunkt der Zustimmung zur Datenschutzerklaerung"),
    )
    marketing_consent = models.BooleanField(
        _("Marketing-Einwilligung"),
        default=False,
        help_text=_("Einwilligung fuer personalisierte Werbung (Art. 6 Abs. 1 lit. a DSGVO)"),
    )
    newsletter_consent = models.BooleanField(
        _("Newsletter-Einwilligung"),
        default=False,
        help_text=_("Einwilligung fuer Newsletter-Versand"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        verbose_name = _("Benutzerprofil")
        verbose_name_plural = _("Benutzerprofile")
        db_table = "accounts_userprofile"
        indexes = [
            models.Index(fields=["subscription_plan"], name="idx_profile_plan"),
            models.Index(
                fields=["subscription_expires_at"],
                name="idx_profile_expires",
            ),
        ]

    def __str__(self):
        return f"Profil: {self.user.email}"

    @property
    def is_premium(self):
        """Check if user has an active premium plan."""
        if self.subscription_plan == self.SubscriptionPlan.FREE:
            return False
        if self.subscription_expires_at and self.subscription_expires_at < timezone.now():
            return False
        return True

    @property
    def full_address(self):
        """Return formatted German address."""
        parts = [self.strasse, f"{self.plz} {self.stadt}".strip()]
        return ", ".join(p for p in parts if p)
```

### Profile Signal

```python
# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
```

---

## documents app

### Document Model

```python
# documents/models.py

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
        default=_("Mein Lebenslauf"),
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


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Manager that includes soft-deleted records."""
    pass


# Add managers to Document (add after the class definition or inside it)
# Document.objects = SoftDeleteManager()
# Document.all_objects = AllObjectsManager()
# Note: In practice, add these as class attributes inside Document:
#   objects = SoftDeleteManager()
#   all_objects = AllObjectsManager()
```

### Template Model

```python
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
```

### Section Model

```python
class Section(models.Model):
    """
    Individual section within a document.
    Sections are ordered and can be toggled visible/invisible.
    Content stored as JSON for flexibility (each section type has its own structure).
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
                # Note: This prevents duplicate section types per document.
                # Remove if users should be allowed multiple sections of same type.
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
```

### Section Content JSON Schemas

```python
"""
JSON content schemas for each section type.
These document the expected structure of Section.content for each SectionType.
Use for validation in forms/serializers.
"""

SECTION_CONTENT_SCHEMAS = {
    "persoenliche_daten": {
        "foto": "",              # URL/path to uploaded photo
        "anrede": "",            # Herr/Frau/Divers
        "vorname": "",
        "nachname": "",
        "geburtsdatum": "",      # YYYY-MM-DD
        "geburtsort": "",
        "staatsangehoerigkeit": "",
        "familienstand": "",     # ledig/verheiratet/geschieden
        "email": "",
        "telefon": "",
        "strasse": "",
        "plz": "",
        "stadt": "",
        "website": "",
        "linkedin": "",
        "xing": "",
    },
    "berufserfahrung": {
        "eintraege": [
            {
                "id": "",                # UUID for HTMX targeting
                "position": "",
                "unternehmen": "",
                "ort": "",
                "von": "",               # YYYY-MM
                "bis": "",               # YYYY-MM or "heute"
                "ist_aktuell": False,
                "beschreibung": "",      # HTML or plain text
                "aufgaben": [],          # List of bullet points
            }
        ]
    },
    "ausbildung": {
        "eintraege": [
            {
                "id": "",
                "abschluss": "",         # e.g. "Bachelor of Science"
                "fachrichtung": "",
                "institution": "",
                "ort": "",
                "von": "",
                "bis": "",
                "note": "",              # e.g. "1,7"
                "beschreibung": "",
            }
        ]
    },
    "kenntnisse": {
        "eintraege": [
            {
                "id": "",
                "name": "",              # e.g. "Microsoft Office"
                "kategorie": "",         # e.g. "Software"
                "niveau": 3,             # 1=Grundkenntnisse, 5=Experte
            }
        ]
    },
    "sprachen": {
        "eintraege": [
            {
                "id": "",
                "sprache": "",           # e.g. "Englisch"
                "niveau": "",            # A1, A2, B1, B2, C1, C2
                "ist_muttersprache": False,
            }
        ]
    },
    "weiterbildungen": {
        "eintraege": [
            {
                "id": "",
                "titel": "",
                "anbieter": "",
                "datum": "",             # YYYY-MM
                "beschreibung": "",
            }
        ]
    },
    "ehrenamt": {
        "eintraege": [
            {
                "id": "",
                "rolle": "",
                "organisation": "",
                "von": "",
                "bis": "",
                "beschreibung": "",
            }
        ]
    },
    "interessen": {
        "eintraege": ["Reisen", "Lesen"],  # Simple string list (tag-style)
    },
    "unterschrift": {
        "ort": "",                   # e.g. "Berlin"
        "datum": "",                 # YYYY-MM-DD (defaults to today)
        "unterschrift_bild": "",     # Optional uploaded signature image
    },
}
```

---

## payments app

### Subscription Model

```python
# payments/models.py

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscription(models.Model):
    """
    Tracks user subscription status synced with Stripe.
    Single active subscription per user enforced at application level.
    """

    class Plan(models.TextChoices):
        FREE = "free", _("Kostenlos")
        PREMIUM_MONTHLY = "premium_monthly", _("Premium Monatlich")
        PREMIUM_YEARLY = "premium_yearly", _("Premium Jährlich")
        BUSINESS = "business", _("Business")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Aktiv")
        PAST_DUE = "past_due", _("Zahlungsverzug")
        CANCELED = "canceled", _("Gekündigt")
        INCOMPLETE = "incomplete", _("Unvollständig")
        TRIALING = "trialing", _("Testphase")
        UNPAID = "unpaid", _("Unbezahlt")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name=_("Benutzer"),
    )
    plan = models.CharField(
        _("Abonnement-Plan"),
        max_length=20,
        choices=Plan.choices,
        default=Plan.FREE,
    )
    stripe_subscription_id = models.CharField(
        _("Stripe Subscription ID"),
        max_length=255,
        blank=True,
        default="",
        unique=True,
        null=True,
    )
    stripe_customer_id = models.CharField(
        _("Stripe Customer ID"),
        max_length=255,
        blank=True,
        default="",
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    current_period_start = models.DateTimeField(
        _("Aktueller Abrechnungszeitraum - Beginn"),
        null=True,
        blank=True,
    )
    current_period_end = models.DateTimeField(
        _("Aktueller Abrechnungszeitraum - Ende"),
        null=True,
        blank=True,
    )
    cancel_at_period_end = models.BooleanField(
        _("Kündigung zum Periodenende"),
        default=False,
        help_text=_("Abonnement laeuft zum Ende der Abrechnungsperiode aus"),
    )

    # Widerrufsrecht tracking
    widerruf_eligible_until = models.DateTimeField(
        _("Widerrufsrecht bis"),
        null=True,
        blank=True,
        help_text=_("14 Tage nach Vertragsabschluss (§ 312g BGB)"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        verbose_name = _("Abonnement")
        verbose_name_plural = _("Abonnements")
        db_table = "payments_subscription"
        indexes = [
            models.Index(fields=["status"], name="idx_sub_status"),
            models.Index(fields=["plan"], name="idx_sub_plan"),
            models.Index(
                fields=["current_period_end"],
                name="idx_sub_period_end",
            ),
            models.Index(
                fields=["stripe_customer_id"],
                name="idx_sub_stripe_cust",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_plan_display()} ({self.get_status_display()})"

    @property
    def is_active(self):
        return self.status in (self.Status.ACTIVE, self.Status.TRIALING)

    @property
    def is_premium(self):
        return self.plan != self.Plan.FREE and self.is_active

    @property
    def can_widerruf(self):
        """Check if withdrawal is still possible (14-day window)."""
        if not self.widerruf_eligible_until:
            return False
        return timezone.now() <= self.widerruf_eligible_until

    @property
    def days_until_widerruf_expires(self):
        """Days remaining for Widerrufsrecht."""
        if not self.can_widerruf:
            return 0
        delta = self.widerruf_eligible_until - timezone.now()
        return max(0, delta.days)
```

### Payment Model

```python
class Payment(models.Model):
    """
    Individual payment record with German MwSt (VAT) breakdown.
    All amounts stored in cents to avoid floating point issues.
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Ausstehend")
        SUCCEEDED = "succeeded", _("Erfolgreich")
        FAILED = "failed", _("Fehlgeschlagen")
        REFUNDED = "refunded", _("Erstattet")
        PARTIALLY_REFUNDED = "partially_refunded", _("Teilweise erstattet")

    class Currency(models.TextChoices):
        EUR = "EUR", _("Euro")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Never delete user with payment history
        related_name="payments",
        verbose_name=_("Benutzer"),
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name=_("Abonnement"),
    )
    stripe_payment_intent_id = models.CharField(
        _("Stripe Payment Intent ID"),
        max_length=255,
        blank=True,
        default="",
        unique=True,
        null=True,
    )

    # Amount fields (stored in cents)
    amount_net = models.PositiveIntegerField(
        _("Nettobetrag (Cent)"),
        help_text=_("Betrag ohne MwSt in Cent"),
    )
    mwst_rate = models.DecimalField(
        _("MwSt-Satz"),
        max_digits=5,
        decimal_places=2,
        default=19.00,
        help_text=_("Mehrwertsteuersatz in Prozent (Standard: 19%)"),
    )
    mwst_amount = models.PositiveIntegerField(
        _("MwSt-Betrag (Cent)"),
        help_text=_("Mehrwertsteuerbetrag in Cent"),
    )
    amount_gross = models.PositiveIntegerField(
        _("Bruttobetrag (Cent)"),
        help_text=_("Gesamtbetrag inkl. MwSt in Cent"),
    )
    currency = models.CharField(
        _("Währung"),
        max_length=3,
        choices=Currency.choices,
        default=Currency.EUR,
    )

    status = models.CharField(
        _("Status"),
        max_length=25,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(
        _("Bezahlt am"),
        null=True,
        blank=True,
    )
    refunded_at = models.DateTimeField(
        _("Erstattet am"),
        null=True,
        blank=True,
    )
    refund_amount = models.PositiveIntegerField(
        _("Erstattungsbetrag (Cent)"),
        default=0,
    )

    # Metadata
    description = models.CharField(
        _("Beschreibung"),
        max_length=255,
        blank=True,
        default="",
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    class Meta:
        verbose_name = _("Zahlung")
        verbose_name_plural = _("Zahlungen")
        db_table = "payments_payment"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="idx_payment_user_date"),
            models.Index(fields=["status"], name="idx_payment_status"),
            models.Index(fields=["paid_at"], name="idx_payment_paid"),
            models.Index(
                fields=["stripe_payment_intent_id"],
                name="idx_payment_stripe_pi",
            ),
        ]

    def __str__(self):
        return f"Zahlung {self.id} - {self.amount_gross_display} ({self.get_status_display()})"

    @property
    def amount_net_display(self):
        """Format net amount for display: '8,40 EUR'"""
        return f"{self.amount_net / 100:.2f} EUR".replace(".", ",")

    @property
    def mwst_amount_display(self):
        return f"{self.mwst_amount / 100:.2f} EUR".replace(".", ",")

    @property
    def amount_gross_display(self):
        return f"{self.amount_gross / 100:.2f} EUR".replace(".", ",")

    @staticmethod
    def calculate_mwst(amount_net_cents, rate=19.00):
        """Calculate MwSt from net amount in cents."""
        from decimal import Decimal, ROUND_HALF_UP
        net = Decimal(str(amount_net_cents))
        rate_decimal = Decimal(str(rate)) / Decimal("100")
        mwst = (net * rate_decimal).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(mwst)
```

### Invoice Model

```python
class Invoice(models.Model):
    """
    GoBD-compliant invoice with sequential numbering.
    Invoice numbers must be sequential with no gaps (GoBD requirement).
    10-year retention period (AO §147).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="invoice",
        verbose_name=_("Zahlung"),
    )
    rechnungsnummer = models.CharField(
        _("Rechnungsnummer"),
        max_length=20,
        unique=True,
        help_text=_("Format: RE-YYYY-NNNNN (fortlaufend, lueckenlos)"),
    )
    rechnungsdatum = models.DateField(
        _("Rechnungsdatum"),
        default=timezone.now,
    )
    leistungszeitraum_start = models.DateField(
        _("Leistungszeitraum Beginn"),
    )
    leistungszeitraum_end = models.DateField(
        _("Leistungszeitraum Ende"),
    )
    pdf_file = models.FileField(
        _("PDF-Rechnung"),
        upload_to="invoices/%Y/%m/",
        blank=True,
        null=True,
    )
    sent_at = models.DateTimeField(
        _("Versendet am"),
        null=True,
        blank=True,
        help_text=_("Zeitpunkt der E-Mail-Zustellung"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("Erstellt am"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Aktualisiert am"), auto_now=True)

    # Retention (AO §147: 10 years)
    retention_until = models.DateField(
        _("Aufbewahrungsfrist bis"),
        null=True,
        blank=True,
        help_text=_("10 Jahre Aufbewahrungspflicht nach AO §147"),
    )

    class Meta:
        verbose_name = _("Rechnung")
        verbose_name_plural = _("Rechnungen")
        db_table = "payments_invoice"
        ordering = ["-rechnungsdatum"]
        indexes = [
            models.Index(
                fields=["rechnungsnummer"],
                name="idx_invoice_number",
            ),
            models.Index(
                fields=["rechnungsdatum"],
                name="idx_invoice_date",
            ),
            models.Index(
                fields=["retention_until"],
                name="idx_invoice_retention",
            ),
        ]

    def __str__(self):
        return self.rechnungsnummer

    def save(self, *args, **kwargs):
        if not self.rechnungsnummer:
            self.rechnungsnummer = self.generate_rechnungsnummer()
        if not self.retention_until:
            self.retention_until = self.rechnungsdatum.replace(
                year=self.rechnungsdatum.year + 10
            )
        super().save(*args, **kwargs)

    @classmethod
    def generate_rechnungsnummer(cls):
        """
        Generate sequential invoice number: RE-YYYY-NNNNN.
        GoBD requires no gaps in numbering.
        """
        import datetime
        year = datetime.date.today().year
        prefix = f"RE-{year}-"

        last_invoice = (
            cls.objects.filter(rechnungsnummer__startswith=prefix)
            .order_by("-rechnungsnummer")
            .first()
        )

        if last_invoice:
            last_number = int(last_invoice.rechnungsnummer.split("-")[-1])
            next_number = last_number + 1
        else:
            next_number = 1

        return f"{prefix}{next_number:05d}"
```

---

## legal app

### CookieConsent Model

```python
# legal/models.py

import uuid
import hashlib
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CookieConsent(models.Model):
    """
    TTDSG §25 compliant cookie consent record.
    Stores each user's consent decision with full audit trail.
    Anonymous users tracked by session_key + hashed IP.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cookie_consents",
        verbose_name=_("Benutzer"),
        help_text=_("NULL fuer anonyme Besucher"),
    )
    session_key = models.CharField(
        _("Session-Key"),
        max_length=40,
        blank=True,
        default="",
    )
    ip_hash = models.CharField(
        _("IP-Hash (SHA256)"),
        max_length=64,
        blank=True,
        default="",
        help_text=_("Gehashte IP-Adresse (nicht rueckverfolgbar)"),
    )
    user_agent = models.TextField(
        _("User Agent"),
        blank=True,
        default="",
    )
    banner_version = models.CharField(
        _("Banner-Version"),
        max_length=10,
        default="1.0",
        help_text=_("Version des Cookie-Banners zum Zeitpunkt der Einwilligung"),
    )

    # Consent categories
    necessary = models.BooleanField(
        _("Notwendige Cookies"),
        default=True,
        help_text=_("Immer aktiv - technisch erforderlich"),
    )
    statistics = models.BooleanField(
        _("Statistik-Cookies"),
        default=False,
    )
    marketing = models.BooleanField(
        _("Marketing-Cookies"),
        default=False,
    )
    external_media = models.BooleanField(
        _("Externe Medien"),
        default=False,
        help_text=_("YouTube, Google Maps, etc."),
    )

    # Timestamp
    consented_at = models.DateTimeField(
        _("Einwilligung erteilt am"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("Cookie-Einwilligung")
        verbose_name_plural = _("Cookie-Einwilligungen")
        db_table = "legal_cookieconsent"
        ordering = ["-consented_at"]
        indexes = [
            models.Index(fields=["user", "-consented_at"], name="idx_consent_user"),
            models.Index(fields=["session_key"], name="idx_consent_session"),
            models.Index(fields=["consented_at"], name="idx_consent_date"),
            models.Index(fields=["banner_version"], name="idx_consent_version"),
        ]

    def __str__(self):
        user_info = self.user.email if self.user else f"Anonym ({self.session_key[:8]})"
        return f"Einwilligung: {user_info} am {self.consented_at}"

    @staticmethod
    def hash_ip(ip_address):
        """Hash IP address with salt for DSGVO compliance (not reversible)."""
        salt = getattr(settings, "COOKIE_CONSENT_IP_SALT", "lebenslauf-salt-change-me")
        return hashlib.sha256(f"{salt}{ip_address}".encode()).hexdigest()
```

### GDPRRequest Model

```python
class GDPRRequest(models.Model):
    """
    Tracks DSGVO/GDPR data subject requests (Art. 15-22 DSGVO).
    Must be processed within 30 days per DSGVO.
    """

    class RequestType(models.TextChoices):
        DATA_ACCESS = "data_access", _("Auskunftsrecht (Art. 15)")
        DATA_EXPORT = "data_export", _("Datenportabilität (Art. 20)")
        DATA_DELETION = "data_deletion", _("Recht auf Löschung (Art. 17)")
        DATA_CORRECTION = "data_correction", _("Recht auf Berichtigung (Art. 16)")
        DATA_RESTRICTION = "data_restriction", _("Recht auf Einschränkung (Art. 18)")
        OBJECTION = "objection", _("Widerspruchsrecht (Art. 21)")

    class Status(models.TextChoices):
        PENDING = "pending", _("Ausstehend")
        IN_PROGRESS = "in_progress", _("In Bearbeitung")
        COMPLETED = "completed", _("Abgeschlossen")
        REJECTED = "rejected", _("Abgelehnt")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Cannot delete user with pending GDPR request
        related_name="gdpr_requests",
        verbose_name=_("Benutzer"),
    )
    request_type = models.CharField(
        _("Antragstyp"),
        max_length=20,
        choices=RequestType.choices,
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField(
        _("Anmerkungen"),
        blank=True,
        default="",
        help_text=_("Interne Notizen zur Bearbeitung"),
    )
    result_file = models.FileField(
        _("Ergebnis-Datei"),
        upload_to="gdpr_exports/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("ZIP-Datei mit exportierten Daten"),
    )

    # Timestamps
    requested_at = models.DateTimeField(
        _("Angefragt am"),
        auto_now_add=True,
    )
    completed_at = models.DateTimeField(
        _("Abgeschlossen am"),
        null=True,
        blank=True,
    )

    # Deadline tracking (DSGVO: 30 days)
    deadline = models.DateTimeField(
        _("Frist"),
        null=True,
        blank=True,
        help_text=_("30 Tage nach Eingang (Art. 12 Abs. 3 DSGVO)"),
    )

    class Meta:
        verbose_name = _("DSGVO-Anfrage")
        verbose_name_plural = _("DSGVO-Anfragen")
        db_table = "legal_gdprrequest"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="idx_gdpr_user_status"),
            models.Index(fields=["status", "deadline"], name="idx_gdpr_deadline"),
            models.Index(fields=["request_type"], name="idx_gdpr_type"),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.user.email} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.deadline and self.requested_at:
            from datetime import timedelta
            self.deadline = self.requested_at + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == self.Status.COMPLETED:
            return False
        if self.deadline:
            from django.utils import timezone
            return timezone.now() > self.deadline
        return False
```

### AuditLog Model

```python
class AuditLog(models.Model):
    """
    Comprehensive audit log for DSGVO compliance.
    Records all data access and modification events.
    Immutable - no update or delete operations should be performed.
    """

    class Action(models.TextChoices):
        CREATE = "create", _("Erstellt")
        UPDATE = "update", _("Aktualisiert")
        DELETE = "delete", _("Gelöscht")
        SOFT_DELETE = "soft_delete", _("Soft-Delete")
        VIEW = "view", _("Angesehen")
        EXPORT = "export", _("Exportiert")
        LOGIN = "login", _("Anmeldung")
        LOGOUT = "logout", _("Abmeldung")
        PASSWORD_CHANGE = "password_change", _("Passwort geändert")
        CONSENT_GIVEN = "consent_given", _("Einwilligung erteilt")
        CONSENT_REVOKED = "consent_revoked", _("Einwilligung widerrufen")
        GDPR_REQUEST = "gdpr_request", _("DSGVO-Anfrage")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("Benutzer"),
    )
    action = models.CharField(
        _("Aktion"),
        max_length=20,
        choices=Action.choices,
    )
    model_name = models.CharField(
        _("Modell"),
        max_length=100,
        blank=True,
        default="",
        help_text=_("Name des betroffenen Django-Modells"),
    )
    object_id = models.CharField(
        _("Objekt-ID"),
        max_length=255,
        blank=True,
        default="",
    )
    changes = models.JSONField(
        _("Änderungen"),
        default=dict,
        blank=True,
        help_text=_("Vorher/Nachher der geaenderten Felder"),
    )
    ip_address = models.GenericIPAddressField(
        _("IP-Adresse"),
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        _("User Agent"),
        blank=True,
        default="",
    )
    timestamp = models.DateTimeField(
        _("Zeitstempel"),
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _("Audit-Protokoll")
        verbose_name_plural = _("Audit-Protokolle")
        db_table = "legal_auditlog"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"], name="idx_audit_user_time"),
            models.Index(fields=["action", "-timestamp"], name="idx_audit_action_time"),
            models.Index(
                fields=["model_name", "object_id"],
                name="idx_audit_model_obj",
            ),
        ]
        # Prevent modifications to audit records
        managed = True

    def __str__(self):
        user_info = self.user.email if self.user else "System"
        return f"[{self.timestamp}] {user_info}: {self.get_action_display()} {self.model_name}"

    def save(self, *args, **kwargs):
        """Only allow creation, not updates."""
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError(_("Audit-Protokolle duerfen nicht geaendert werden."))
        super().save(*args, **kwargs)

    @classmethod
    def log(cls, user, action, model_name="", object_id="", changes=None,
            ip_address=None, user_agent=""):
        """Convenience method to create an audit log entry."""
        return cls.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
```

---

## Admin Registration

```python
# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Profil"
    verbose_name_plural = "Profile"
    fieldsets = (
        ("Persönliche Daten", {
            "fields": ("anrede", "geburtsdatum", "telefon"),
        }),
        ("Adresse", {
            "fields": ("strasse", "plz", "stadt", "bundesland"),
        }),
        ("Abonnement", {
            "fields": ("subscription_plan", "subscription_expires_at"),
        }),
        ("DSGVO", {
            "fields": (
                "privacy_accepted_at",
                "marketing_consent",
                "newsletter_consent",
            ),
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "date_joined")
    list_filter = ("is_staff", "is_active", "is_email_verified")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    inlines = [UserProfileInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Persönliche Informationen", {"fields": ("first_name", "last_name")}),
        ("Berechtigungen", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_email_verified",
                       "groups", "user_permissions"),
        }),
        ("Wichtige Daten", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )


# documents/admin.py

from django.contrib import admin
from .models import Document, Template, Section


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "doc_type", "template", "created_at", "is_deleted")
    list_filter = ("doc_type", "is_premium", "deleted_at")
    search_fields = ("title", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_premium", "is_active", "ordering")
    list_filter = ("category", "is_premium", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("ordering", "is_active")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("section_type", "document", "ordering", "is_visible")
    list_filter = ("section_type", "is_visible")


# payments/admin.py

from django.contrib import admin
from .models import Subscription, Payment, Invoice


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "current_period_end", "cancel_at_period_end")
    list_filter = ("plan", "status", "cancel_at_period_end")
    search_fields = ("user__email", "stripe_subscription_id")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "amount_gross_display", "status", "paid_at", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("user__email", "stripe_payment_intent_id")
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("rechnungsnummer", "rechnungsdatum", "payment", "sent_at")
    search_fields = ("rechnungsnummer",)
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "rechnungsdatum"


# legal/admin.py

from django.contrib import admin
from .models import CookieConsent, GDPRRequest, AuditLog


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "necessary", "statistics", "marketing",
                    "external_media", "banner_version", "consented_at")
    list_filter = ("statistics", "marketing", "external_media", "banner_version")
    readonly_fields = ("id", "consented_at", "ip_hash")
    date_hierarchy = "consented_at"


@admin.register(GDPRRequest)
class GDPRRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "request_type", "status", "requested_at",
                    "deadline", "is_overdue")
    list_filter = ("request_type", "status")
    search_fields = ("user__email",)
    readonly_fields = ("id", "requested_at")
    date_hierarchy = "requested_at"

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = "Überfällig"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_id")
    list_filter = ("action", "model_name")
    search_fields = ("user__email", "model_name", "object_id")
    readonly_fields = ("id", "user", "action", "model_name", "object_id",
                       "changes", "ip_address", "user_agent", "timestamp")
    date_hierarchy = "timestamp"

    def has_change_permission(self, request, obj=None):
        return False  # Audit logs are immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Audit logs cannot be deleted
```

---

## Migrations Note

After defining all models, generate migrations in the correct order:

```bash
python manage.py makemigrations accounts
python manage.py makemigrations documents
python manage.py makemigrations payments
python manage.py makemigrations legal
python manage.py migrate
```

The `accounts` app must be migrated first since other models reference `AUTH_USER_MODEL`.
