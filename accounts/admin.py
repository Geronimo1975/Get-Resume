from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.admin import StackedInline
from unfold.decorators import action, display

from .models import User, UserProfile


class UserProfileInline(StackedInline):
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
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = (
        "email", "first_name", "last_name",
        "display_staff", "display_verified", "display_subscription",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "is_email_verified")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
    inlines = [UserProfileInline]
    actions_detail = ["admin_mark_verified", "admin_resend_confirmation"]

    compressed_fields = True
    warn_unsaved_form = True
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Persönliche Informationen", {"fields": ("first_name", "last_name")}),
        ("Berechtigungen", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_email_verified",
                       "groups", "user_permissions"),
            "classes": ["collapse"],
        }),
        ("Wichtige Daten", {
            "fields": ("last_login", "date_joined"),
            "classes": ["collapse"],
        }),
    )
    readonly_fields = ("last_login", "date_joined")
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )

    @display(
        description="Mitarbeiter",
        label={
            True: "success",
            False: "info",
        },
    )
    def display_staff(self, obj):
        return obj.is_staff

    @display(
        description="E-Mail bestätigt",
        label={
            True: "success",
            False: "warning",
        },
    )
    def display_verified(self, obj):
        return obj.is_email_verified

    @display(
        description="Abonnement",
        label={
            "free": "info",
            "premium_monthly": "success",
            "premium_yearly": "success",
            "business": "warning",
        },
    )
    def display_subscription(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.subscription_plan
        return "free"

    @action(description="E-Mail als bestätigt markieren")
    def admin_mark_verified(self, request, object_id):
        user = User.objects.get(pk=object_id)
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        # Also confirm in allauth's EmailAddress table
        try:
            from allauth.account.models import EmailAddress

            email_address, created = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": True, "primary": True},
            )
            if not created:
                email_address.verified = True
                email_address.primary = True
                email_address.save(update_fields=["verified", "primary"])
        except Exception:
            pass

        from django.contrib import messages
        messages.success(request, f"E-Mail für {user.email} als bestätigt markiert.")

    @action(description="Bestätigungsmail erneut senden")
    def admin_resend_confirmation(self, request, object_id):
        user = User.objects.get(pk=object_id)

        from django.contrib import messages

        if user.is_email_verified:
            messages.warning(request, f"{user.email} ist bereits bestätigt.")
            return

        try:
            from allauth.account.models import EmailAddress
            from allauth.account.utils import send_email_confirmation

            # Ensure EmailAddress exists
            EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": False, "primary": True},
            )
            send_email_confirmation(request, user)
            messages.success(request, f"Bestätigungsmail an {user.email} gesendet.")
        except Exception as e:
            messages.error(request, f"Fehler beim Senden: {e}")
