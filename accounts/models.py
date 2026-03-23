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
    username = None
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
