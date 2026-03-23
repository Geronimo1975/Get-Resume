# GDPR Implementation Reference

Complete DSGVO/GDPR implementation code including middleware, views, management commands, and signals.

---

## 1. CookieConsentMiddleware

Server-side middleware that blocks tracking scripts before user has given consent (TTDSG 25).

```python
# legal/middleware.py

import json
import logging
from django.conf import settings
from django.urls import resolve, reverse

logger = logging.getLogger(__name__)

# Pages that should never be blocked by cookie consent
EXEMPT_URL_NAMES = [
    "legal:impressum",
    "legal:datenschutz",
    "legal:agb",
    "legal:widerrufsbelehrung",
    "legal:cookie_banner",
    "legal:cookie_consent_save",
    "legal:cookie_settings",
    "legal:cookie_details",
    "legal:cookie_consent_revoke",
    "health_check",
]

EXEMPT_URL_PREFIXES = [
    "/admin-dashboard/",
    "/static/",
    "/media/",
]


class CookieConsentMiddleware:
    """
    TTDSG §25 compliant middleware.

    - Reads the cookie_consent cookie from the request
    - Injects consent status into request object for use in templates/views
    - Blocks tracking-related response headers/scripts if consent not given
    - Bypasses legal pages and static assets

    The actual blocking of third-party scripts happens in templates via
    {% if request.cookie_consent.statistics %} conditionals.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.cookie_name = getattr(settings, "COOKIE_CONSENT_NAME", "cookie_consent")

    def __call__(self, request):
        # Parse consent from cookie
        request.cookie_consent = self._parse_consent(request)
        request.cookie_consent_given = request.cookie_consent.get("given", False)

        response = self.get_response(request)

        # Remove tracking headers if no consent
        if not request.cookie_consent_given:
            self._strip_tracking_headers(response)

        return response

    def _parse_consent(self, request):
        """
        Parse the cookie_consent cookie value.
        Returns a dict with boolean values for each category.
        """
        cookie_value = request.COOKIES.get(self.cookie_name, "")

        if not cookie_value:
            return {
                "given": False,
                "necessary": True,   # Always true
                "statistics": False,
                "marketing": False,
                "external_media": False,
            }

        try:
            consent = json.loads(cookie_value)
            return {
                "given": True,
                "necessary": True,  # Always true regardless of cookie value
                "statistics": consent.get("statistics", False),
                "marketing": consent.get("marketing", False),
                "external_media": consent.get("external_media", False),
            }
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Invalid cookie_consent cookie value: %s", cookie_value[:100])
            return {
                "given": False,
                "necessary": True,
                "statistics": False,
                "marketing": False,
                "external_media": False,
            }

    def _strip_tracking_headers(self, response):
        """Remove any tracking-related headers from response if no consent."""
        tracking_headers = [
            "X-Analytics-ID",
            "X-Marketing-Pixel",
        ]
        for header in tracking_headers:
            if header in response:
                del response[header]

    def _is_exempt(self, request):
        """Check if the current request is exempt from consent checks."""
        path = request.path

        # Check prefix exemptions
        for prefix in EXEMPT_URL_PREFIXES:
            if path.startswith(prefix):
                return True

        # Check named URL exemptions
        try:
            resolved = resolve(path)
            url_name = f"{resolved.namespace}:{resolved.url_name}" if resolved.namespace else resolved.url_name
            if url_name in EXEMPT_URL_NAMES:
                return True
        except Exception:
            pass

        return False
```

---

## 2. Cookie Consent Context Processor

```python
# legal/context_processors.py

def cookie_consent(request):
    """
    Inject cookie consent status into all templates.
    Use in templates: {% if request.cookie_consent.statistics %}
    """
    return {
        "cookie_consent_given": getattr(request, "cookie_consent_given", False),
        "cookie_consent": getattr(request, "cookie_consent", {
            "given": False,
            "necessary": True,
            "statistics": False,
            "marketing": False,
            "external_media": False,
        }),
    }
```

---

## 3. Cookie Consent HTMX Views

```python
# legal/views.py

import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import CookieConsent, AuditLog

logger = logging.getLogger(__name__)


class CookieBannerView(TemplateView):
    """Render the initial cookie banner (Layer 1)."""
    template_name = "legal/includes/cookie_banner.html"


class CookieSettingsView(TemplateView):
    """Render cookie settings panel (Layer 2) — loaded via HTMX."""
    template_name = "legal/includes/cookie_settings.html"


class CookieDetailsView(TemplateView):
    """Render detailed cookie table (Layer 3) — loaded via HTMX."""
    template_name = "legal/includes/cookie_details.html"


class CookieConsentSaveView(View):
    """
    Save cookie consent choices.
    Called via HTMX POST from the cookie banner.
    Stores consent in:
    1. First-party cookie (for middleware to read on next request)
    2. Database record (for audit/compliance log)
    """

    def post(self, request):
        # Parse consent choices from form data
        consent = {
            "necessary": True,  # Always true
            "statistics": request.POST.get("statistics") in ("true", "on", "True"),
            "marketing": request.POST.get("marketing") in ("true", "on", "True"),
            "external_media": request.POST.get("external_media") in ("true", "on", "True"),
        }

        # Store in database for audit trail
        ip_hash = CookieConsent.hash_ip(self._get_client_ip(request))
        banner_version = getattr(
            settings, "COOKIE_CONSENT_BANNER_VERSION", "1.0"
        )

        consent_record = CookieConsent.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key or "",
            ip_hash=ip_hash,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            banner_version=banner_version,
            necessary=True,
            statistics=consent["statistics"],
            marketing=consent["marketing"],
            external_media=consent["external_media"],
        )

        # Audit log
        AuditLog.log(
            user=request.user if request.user.is_authenticated else None,
            action=AuditLog.Action.CONSENT_GIVEN,
            model_name="CookieConsent",
            object_id=str(consent_record.id),
            changes=consent,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        # Create response (dismiss the banner)
        response = HttpResponse(
            '<div id="cookie-banner" class="hidden"></div>'
        )

        # Set first-party cookie
        cookie_name = getattr(settings, "COOKIE_CONSENT_NAME", "cookie_consent")
        max_age = getattr(settings, "COOKIE_CONSENT_MAX_AGE", 365 * 24 * 60 * 60)

        response.set_cookie(
            cookie_name,
            json.dumps(consent),
            max_age=max_age,
            httponly=False,  # Needs to be readable by JS for conditional script loading
            samesite="Lax",
            secure=not settings.DEBUG,
        )

        return response

    def _get_client_ip(self, request):
        """Extract client IP, considering proxy headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")


class CookieConsentRevokeView(LoginRequiredMixin, View):
    """
    Revoke all cookie consents.
    Deletes the consent cookie and logs the revocation.
    """

    def post(self, request):
        cookie_name = getattr(settings, "COOKIE_CONSENT_NAME", "cookie_consent")

        # Log revocation
        AuditLog.log(
            user=request.user,
            action=AuditLog.Action.CONSENT_REVOKED,
            model_name="CookieConsent",
            ip_address=request.META.get("REMOTE_ADDR", ""),
        )

        # Return response with cookie deleted
        response = HttpResponse(
            '<div id="cookie-banner">'
            '<p class="text-center p-4 text-green-700">'
            'Ihre Cookie-Einstellungen wurden zurückgesetzt. '
            'Beim nächsten Seitenaufruf wird das Cookie-Banner erneut angezeigt.'
            '</p></div>'
        )
        response.delete_cookie(cookie_name)
        return response
```

---

## 4. GDPR Data Rights Views

```python
# legal/views.py (continued)

import io
import zipfile
import json
from datetime import timedelta

from django.http import FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.utils import timezone
from django.template.loader import render_to_string

from .models import GDPRRequest, AuditLog
from accounts.models import UserProfile
from documents.models import Document, Section
from payments.models import Payment, Invoice, Subscription


class DataAccessView(LoginRequiredMixin, View):
    """
    Art. 15 DSGVO — Auskunftsrecht.
    Shows the user all data stored about them.
    Provides JSON download option.
    """

    def get(self, request):
        # Compile all user data
        user_data = self._compile_user_data(request.user)
        return render(request, "legal/data_access.html", {
            "user_data": user_data,
        })

    def _compile_user_data(self, user):
        """Compile all personal data for a user into a dict."""
        profile = getattr(user, "profile", None)

        data = {
            "konto": {
                "email": user.email,
                "vorname": user.first_name,
                "nachname": user.last_name,
                "registriert_am": user.date_joined.isoformat(),
                "letzte_anmeldung": user.last_login.isoformat() if user.last_login else None,
            },
        }

        if profile:
            data["profil"] = {
                "anrede": profile.get_anrede_display(),
                "geburtsdatum": str(profile.geburtsdatum) if profile.geburtsdatum else None,
                "telefon": profile.telefon,
                "strasse": profile.strasse,
                "plz": profile.plz,
                "stadt": profile.stadt,
                "bundesland": profile.get_bundesland_display() if profile.bundesland else None,
                "abonnement": profile.get_subscription_plan_display(),
                "sprache": profile.get_preferred_language_display(),
                "datenschutz_akzeptiert_am": (
                    profile.privacy_accepted_at.isoformat()
                    if profile.privacy_accepted_at else None
                ),
                "marketing_einwilligung": profile.marketing_consent,
                "newsletter_einwilligung": profile.newsletter_consent,
            }

        # Documents
        documents = Document.objects.filter(user=user, deleted_at__isnull=True)
        data["dokumente"] = [
            {
                "id": str(doc.id),
                "typ": doc.get_doc_type_display(),
                "titel": doc.title,
                "erstellt_am": doc.created_at.isoformat(),
                "aktualisiert_am": doc.updated_at.isoformat(),
                "abschnitte": [
                    {
                        "typ": s.get_section_type_display(),
                        "inhalt": s.content,
                    }
                    for s in doc.sections.all()
                ],
            }
            for doc in documents
        ]

        # Payments
        payments = Payment.objects.filter(user=user)
        data["zahlungen"] = [
            {
                "betrag_brutto": p.amount_gross_display,
                "status": p.get_status_display(),
                "bezahlt_am": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p in payments
        ]

        # Cookie consents
        consents = CookieConsent.objects.filter(user=user)
        data["cookie_einwilligungen"] = [
            {
                "statistik": c.statistics,
                "marketing": c.marketing,
                "externe_medien": c.external_media,
                "erteilt_am": c.consented_at.isoformat(),
                "banner_version": c.banner_version,
            }
            for c in consents
        ]

        return data


class DataExportView(LoginRequiredMixin, View):
    """
    Art. 20 DSGVO — Datenportabilitaet.
    Compiles all user data into a ZIP file (JSON + PDF documents).
    """

    def post(self, request):
        user = request.user

        # Check for recent export request (rate limiting)
        recent_request = GDPRRequest.objects.filter(
            user=user,
            request_type=GDPRRequest.RequestType.DATA_EXPORT,
            requested_at__gte=timezone.now() - timedelta(hours=24),
        ).exists()

        if recent_request:
            messages.warning(
                request,
                "Sie haben in den letzten 24 Stunden bereits einen Datenexport angefordert. "
                "Bitte versuchen Sie es spaeter erneut."
            )
            return redirect("legal:data_access")

        # Create GDPR request record
        gdpr_request = GDPRRequest.objects.create(
            user=user,
            request_type=GDPRRequest.RequestType.DATA_EXPORT,
            status=GDPRRequest.Status.IN_PROGRESS,
        )

        # Compile data
        data_view = DataAccessView()
        user_data = data_view._compile_user_data(user)

        # Create ZIP file
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add JSON data export
            zf.writestr(
                "meine_daten.json",
                json.dumps(user_data, indent=2, ensure_ascii=False, default=str),
            )

            # Add document PDFs
            documents = Document.objects.filter(user=user, deleted_at__isnull=True)
            for doc in documents:
                if doc.pdf_file:
                    try:
                        zf.writestr(
                            f"dokumente/{doc.title}_{doc.id}.pdf",
                            doc.pdf_file.read(),
                        )
                    except Exception:
                        logger.exception("Failed to include PDF for document %s", doc.id)

            # Add invoice PDFs
            invoices = Invoice.objects.filter(payment__user=user)
            for invoice in invoices:
                if invoice.pdf_file:
                    try:
                        zf.writestr(
                            f"rechnungen/{invoice.rechnungsnummer}.pdf",
                            invoice.pdf_file.read(),
                        )
                    except Exception:
                        logger.exception("Failed to include invoice %s", invoice.rechnungsnummer)

            # Add README explaining the export
            readme = (
                "Datenexport - Lebenslauf-Builder\n"
                "================================\n\n"
                f"Exportiert am: {timezone.now().strftime('%d.%m.%Y %H:%M Uhr')}\n"
                f"Benutzer: {user.email}\n\n"
                "Enthaltene Dateien:\n"
                "- meine_daten.json: Alle gespeicherten persoenlichen Daten\n"
                "- dokumente/: Ihre Lebenslauf-PDFs\n"
                "- rechnungen/: Ihre Rechnungen\n\n"
                "Bei Fragen wenden Sie sich an: datenschutz@lebenslauf-builder.de\n"
            )
            zf.writestr("README.txt", readme)

        buffer.seek(0)

        # Update request status
        gdpr_request.status = GDPRRequest.Status.COMPLETED
        gdpr_request.completed_at = timezone.now()
        gdpr_request.save()

        # Audit log
        AuditLog.log(
            user=user,
            action=AuditLog.Action.EXPORT,
            model_name="User",
            object_id=str(user.id),
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        # Return ZIP download
        filename = f"datenexport_{user.email}_{timezone.now().strftime('%Y%m%d')}.zip"
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/zip",
        )


class DataDeletionView(LoginRequiredMixin, View):
    """
    Art. 17 DSGVO — Recht auf Loeschung.
    Initiates soft delete of all user data.
    Hard delete scheduled after 30-day grace period.
    """

    def get(self, request):
        """Show deletion confirmation page."""
        # Check for active subscription
        has_active_sub = hasattr(request.user, "subscription") and request.user.subscription.is_active
        # Check for pending invoices within retention period
        has_retained_invoices = Invoice.objects.filter(
            payment__user=request.user,
            retention_until__gt=timezone.now().date(),
        ).exists()

        return render(request, "legal/data_deletion.html", {
            "has_active_subscription": has_active_sub,
            "has_retained_invoices": has_retained_invoices,
        })

    def post(self, request):
        """Process deletion request."""
        user = request.user

        # Verify password for security
        password = request.POST.get("password", "")
        if not user.check_password(password):
            messages.error(request, "Das eingegebene Passwort ist nicht korrekt.")
            return redirect("legal:data_deletion")

        # Verify confirmation checkbox
        if not request.POST.get("confirm_deletion"):
            messages.error(request, "Bitte bestätigen Sie die Löschung.")
            return redirect("legal:data_deletion")

        # Create GDPR deletion request
        gdpr_request = GDPRRequest.objects.create(
            user=user,
            request_type=GDPRRequest.RequestType.DATA_DELETION,
            status=GDPRRequest.Status.IN_PROGRESS,
            notes="Nutzer hat Löschung über die Website beantragt.",
        )

        # Soft-delete all documents
        Document.objects.filter(user=user, deleted_at__isnull=True).update(
            deleted_at=timezone.now()
        )

        # Cancel active subscription
        if hasattr(user, "subscription") and user.subscription.is_active:
            from payments.services import StripeService
            stripe_service = StripeService()
            try:
                stripe_service.cancel_subscription(user.subscription.stripe_subscription_id)
            except Exception:
                logger.exception("Failed to cancel Stripe subscription for user %s", user.id)

        # Clear profile data (but keep account for grace period)
        if hasattr(user, "profile"):
            profile = user.profile
            profile.telefon = ""
            profile.strasse = ""
            profile.plz = ""
            profile.stadt = ""
            profile.bundesland = ""
            profile.geburtsdatum = None
            profile.marketing_consent = False
            profile.newsletter_consent = False
            profile.save()

        # Deactivate user account
        user.is_active = False
        user.save(update_fields=["is_active"])

        # Schedule hard delete via Celery (30 days)
        from legal.tasks import hard_delete_user_data
        hard_delete_user_data.apply_async(
            args=[str(user.id), str(gdpr_request.id)],
            countdown=30 * 24 * 60 * 60,  # 30 days in seconds
        )

        # Audit log
        AuditLog.log(
            user=user,
            action=AuditLog.Action.GDPR_REQUEST,
            model_name="User",
            object_id=str(user.id),
            changes={"request_type": "data_deletion", "status": "soft_deleted"},
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        # Send confirmation email
        from django.core.mail import send_mail
        send_mail(
            subject="Bestätigung Ihrer Löschanfrage - Lebenslauf-Builder",
            message=(
                f"Sehr geehrte(r) {user.get_full_name()},\n\n"
                "wir bestätigen den Eingang Ihrer Löschanfrage. Ihr Konto wurde deaktiviert "
                "und Ihre persönlichen Daten werden innerhalb von 30 Tagen endgültig gelöscht.\n\n"
                "Bitte beachten Sie, dass Rechnungsdaten aufgrund der gesetzlichen "
                "Aufbewahrungspflicht (AO §147) für 10 Jahre aufbewahrt werden müssen.\n\n"
                "Falls Sie Ihre Anfrage innerhalb der 30-Tage-Frist zurücknehmen möchten, "
                "kontaktieren Sie uns bitte unter datenschutz@lebenslauf-builder.de.\n\n"
                "Mit freundlichen Grüßen\n"
                "Ihr Lebenslauf-Builder Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        # Log the user out
        from django.contrib.auth import logout
        logout(request)

        messages.success(
            request,
            "Ihre Löschanfrage wurde erfolgreich eingereicht. "
            "Sie erhalten eine Bestätigung per E-Mail."
        )
        return redirect("legal:impressum")
```

---

## 5. Celery Tasks for GDPR

```python
# legal/tasks.py

import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue="gdpr")
def hard_delete_user_data(self, user_id, gdpr_request_id):
    """
    Hard delete user data after 30-day grace period.
    Preserves invoice data per AO §147 (10-year retention).
    """
    from django.contrib.auth import get_user_model
    from documents.models import Document
    from legal.models import GDPRRequest, AuditLog, CookieConsent
    from payments.models import Invoice

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        gdpr_request = GDPRRequest.objects.get(id=gdpr_request_id)
    except (User.DoesNotExist, GDPRRequest.DoesNotExist):
        logger.error("User %s or GDPR request %s not found", user_id, gdpr_request_id)
        return

    # Double-check the user is still deactivated (they may have reactivated)
    if user.is_active:
        logger.info("User %s has been reactivated, skipping hard delete", user_id)
        gdpr_request.status = GDPRRequest.Status.REJECTED
        gdpr_request.notes += "\nNutzer hat das Konto vor Ablauf der Frist reaktiviert."
        gdpr_request.save()
        return

    # Hard delete documents and their files
    documents = Document.all_objects.filter(user=user)
    for doc in documents:
        if doc.pdf_file:
            doc.pdf_file.delete(save=False)
        # Delete sections
        doc.sections.all().delete()
    documents.delete()

    # Delete cookie consents
    CookieConsent.objects.filter(user=user).delete()

    # Anonymize audit logs (keep structure but remove PII)
    AuditLog.objects.filter(user=user).update(
        user=None,
        ip_address=None,
        user_agent="[GDPR DELETED]",
    )

    # Delete profile
    if hasattr(user, "profile"):
        user.profile.delete()

    # NOTE: Invoices are NOT deleted (10-year retention AO §147)
    # But we anonymize the user reference
    retained_invoices = Invoice.objects.filter(payment__user=user)
    if retained_invoices.exists():
        logger.info(
            "Retaining %d invoices for user %s (AO §147)",
            retained_invoices.count(),
            user_id,
        )

    # Anonymize user record (keep for invoice FK, anonymize PII)
    user.email = f"deleted-{user.id}@anonymized.local"
    user.first_name = "[Gelöscht]"
    user.last_name = "[Gelöscht]"
    user.set_unusable_password()
    user.save()

    # Update GDPR request
    gdpr_request.status = GDPRRequest.Status.COMPLETED
    gdpr_request.completed_at = timezone.now()
    gdpr_request.notes += f"\nHard delete durchgeführt am {timezone.now().isoformat()}"
    gdpr_request.save()

    logger.info("Hard delete completed for user %s", user_id)


@shared_task(queue="gdpr")
def gdpr_cleanup_soft_deleted():
    """
    Daily cleanup task: remove expired soft-deleted records.
    Runs documents that have been soft-deleted for more than 90 days
    and have no pending GDPR deletion request.
    """
    from documents.models import Document

    cutoff = timezone.now() - timedelta(days=90)

    expired_documents = Document.all_objects.filter(
        deleted_at__isnull=False,
        deleted_at__lt=cutoff,
    )

    count = 0
    for doc in expired_documents:
        if doc.pdf_file:
            doc.pdf_file.delete(save=False)
        doc.sections.all().delete()
        doc.delete()
        count += 1

    if count > 0:
        logger.info("GDPR cleanup: removed %d expired soft-deleted documents", count)


@shared_task(queue="gdpr")
def check_overdue_gdpr_requests():
    """
    Check for GDPR requests that have exceeded the 30-day deadline.
    Sends alert to admin team.
    """
    from legal.models import GDPRRequest
    from django.core.mail import mail_admins

    overdue = GDPRRequest.objects.filter(
        status__in=[GDPRRequest.Status.PENDING, GDPRRequest.Status.IN_PROGRESS],
        deadline__lt=timezone.now(),
    )

    if overdue.exists():
        details = "\n".join(
            f"- {r.user.email}: {r.get_request_type_display()} "
            f"(angefragt am {r.requested_at.strftime('%d.%m.%Y')}, "
            f"Frist: {r.deadline.strftime('%d.%m.%Y')})"
            for r in overdue
        )
        mail_admins(
            subject=f"DSGVO-WARNUNG: {overdue.count()} überfällige Anfragen",
            message=(
                f"Die folgenden DSGVO-Anfragen haben die 30-Tage-Frist überschritten:\n\n"
                f"{details}\n\n"
                f"Bitte umgehend bearbeiten! (Art. 12 Abs. 3 DSGVO)"
            ),
        )
        logger.warning("Found %d overdue GDPR requests!", overdue.count())
```

---

## 6. Management Commands

### gdpr_cleanup

```python
# legal/management/commands/gdpr_cleanup.py

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from documents.models import Document
from legal.models import CookieConsent


class Command(BaseCommand):
    help = (
        "DSGVO Cleanup: Delete expired soft-deleted documents and old anonymous "
        "cookie consent records. Run daily via cron or Celery Beat."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--document-days",
            type=int,
            default=90,
            help="Delete soft-deleted documents older than N days (default: 90)",
        )
        parser.add_argument(
            "--consent-days",
            type=int,
            default=730,
            help="Delete anonymous cookie consent records older than N days (default: 730 = 2 years)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — keine Daten werden gelöscht\n"))

        # 1. Cleanup soft-deleted documents
        doc_cutoff = timezone.now() - timedelta(days=options["document_days"])
        expired_docs = Document.all_objects.filter(
            deleted_at__isnull=False,
            deleted_at__lt=doc_cutoff,
        )
        doc_count = expired_docs.count()

        if not dry_run and doc_count > 0:
            for doc in expired_docs:
                if doc.pdf_file:
                    doc.pdf_file.delete(save=False)
                doc.sections.all().delete()
            expired_docs.delete()

        self.stdout.write(
            f"Dokumente: {doc_count} abgelaufene soft-deleted Dokumente "
            f"{'würden gelöscht' if dry_run else 'gelöscht'}"
        )

        # 2. Cleanup old anonymous cookie consents
        consent_cutoff = timezone.now() - timedelta(days=options["consent_days"])
        old_consents = CookieConsent.objects.filter(
            user__isnull=True,
            consented_at__lt=consent_cutoff,
        )
        consent_count = old_consents.count()

        if not dry_run and consent_count > 0:
            old_consents.delete()

        self.stdout.write(
            f"Cookie-Consents: {consent_count} alte anonyme Einträge "
            f"{'würden gelöscht' if dry_run else 'gelöscht'}"
        )

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"\nGDPR Cleanup abgeschlossen: "
            f"{doc_count} Dokumente, {consent_count} Cookie-Consents"
        ))
```

### consent_audit

```python
# legal/management/commands/consent_audit.py

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from legal.models import CookieConsent, GDPRRequest, AuditLog


class Command(BaseCommand):
    help = "Generate DSGVO compliance audit report for the specified time period."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Report period in days (default: 30)",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="",
            help="Output file path (default: stdout)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        since = timezone.now() - timedelta(days=days)

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DSGVO COMPLIANCE AUDIT REPORT")
        report_lines.append(f"Zeitraum: {since.strftime('%d.%m.%Y')} bis {timezone.now().strftime('%d.%m.%Y')}")
        report_lines.append("=" * 60)

        # Cookie Consent Statistics
        report_lines.append("\n--- Cookie-Einwilligungen ---")
        consents = CookieConsent.objects.filter(consented_at__gte=since)
        total = consents.count()
        stats = consents.aggregate(
            statistics_yes=Count("id", filter=Q(statistics=True)),
            marketing_yes=Count("id", filter=Q(marketing=True)),
            external_media_yes=Count("id", filter=Q(external_media=True)),
        )
        report_lines.append(f"Gesamt: {total}")
        if total > 0:
            report_lines.append(
                f"Statistik akzeptiert: {stats['statistics_yes']} ({stats['statistics_yes']/total*100:.1f}%)"
            )
            report_lines.append(
                f"Marketing akzeptiert: {stats['marketing_yes']} ({stats['marketing_yes']/total*100:.1f}%)"
            )
            report_lines.append(
                f"Externe Medien akzeptiert: {stats['external_media_yes']} ({stats['external_media_yes']/total*100:.1f}%)"
            )

        # Banner versions in use
        versions = consents.values("banner_version").annotate(count=Count("id")).order_by("-count")
        report_lines.append(f"\nBanner-Versionen:")
        for v in versions:
            report_lines.append(f"  v{v['banner_version']}: {v['count']} Einwilligungen")

        # GDPR Requests
        report_lines.append("\n--- DSGVO-Anfragen ---")
        requests = GDPRRequest.objects.filter(requested_at__gte=since)
        by_type = requests.values("request_type").annotate(count=Count("id"))
        for rt in by_type:
            report_lines.append(f"  {rt['request_type']}: {rt['count']}")

        # Overdue requests
        overdue = GDPRRequest.objects.filter(
            status__in=["pending", "in_progress"],
            deadline__lt=timezone.now(),
        )
        if overdue.exists():
            report_lines.append(f"\n  *** WARNUNG: {overdue.count()} überfällige Anfragen! ***")
            for r in overdue:
                report_lines.append(
                    f"    - {r.user.email}: {r.get_request_type_display()} "
                    f"(Frist: {r.deadline.strftime('%d.%m.%Y')})"
                )

        # Audit Log Summary
        report_lines.append("\n--- Audit-Protokoll ---")
        logs = AuditLog.objects.filter(timestamp__gte=since)
        by_action = logs.values("action").annotate(count=Count("id")).order_by("-count")
        for a in by_action:
            report_lines.append(f"  {a['action']}: {a['count']}")

        report_lines.append("\n" + "=" * 60)
        report_lines.append("Ende des Berichts")
        report_lines.append("=" * 60)

        report = "\n".join(report_lines)

        # Output
        if options["output"]:
            with open(options["output"], "w") as f:
                f.write(report)
            self.stdout.write(self.style.SUCCESS(f"Bericht gespeichert: {options['output']}"))
        else:
            self.stdout.write(report)
```

---

## 7. Django Signals for Automatic Audit Logging

```python
# legal/signals.py

import logging
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

from .models import AuditLog

logger = logging.getLogger(__name__)

# Models to automatically audit
AUDITED_MODELS = [
    "accounts.User",
    "accounts.UserProfile",
    "documents.Document",
    "documents.Section",
    "payments.Subscription",
    "payments.Payment",
    "legal.CookieConsent",
]


def _get_model_label(instance):
    """Get 'app_label.ModelName' string from a model instance."""
    return f"{instance._meta.app_label}.{instance.__class__.__name__}"


def _get_changes(instance):
    """
    Detect field changes on a model instance.
    Only works for update operations (not create).
    """
    if not instance.pk:
        return {}

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return {}

    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(instance, field_name)
        if old_value != new_value:
            # Do not log sensitive field values
            if field_name in ("password",):
                changes[field_name] = {"old": "[REDACTED]", "new": "[REDACTED]"}
            else:
                changes[field_name] = {
                    "old": str(old_value),
                    "new": str(new_value),
                }

    return changes


@receiver(post_save)
def audit_model_save(sender, instance, created, **kwargs):
    """Automatically log create/update operations on audited models."""
    model_label = _get_model_label(instance)
    if model_label not in AUDITED_MODELS:
        return

    # Skip audit log entries themselves to prevent infinite recursion
    if isinstance(instance, AuditLog):
        return

    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE

    # Determine user from instance
    user = None
    if hasattr(instance, "user_id"):
        user = instance.user if hasattr(instance, "user") else None
    elif hasattr(instance, "id") and model_label == "accounts.User":
        user = instance

    changes = {} if created else _get_changes(instance)

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_label,
            object_id=str(instance.pk),
            changes=changes,
        )
    except Exception:
        logger.exception("Failed to create audit log for %s %s", model_label, instance.pk)


@receiver(pre_delete)
def audit_model_delete(sender, instance, **kwargs):
    """Log delete operations on audited models."""
    model_label = _get_model_label(instance)
    if model_label not in AUDITED_MODELS:
        return
    if isinstance(instance, AuditLog):
        return

    user = None
    if hasattr(instance, "user"):
        user = instance.user
    elif model_label == "accounts.User":
        user = instance

    try:
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.DELETE,
            model_name=model_label,
            object_id=str(instance.pk),
        )
    except Exception:
        logger.exception("Failed to create audit log for delete %s %s", model_label, instance.pk)


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    """Log user login events."""
    AuditLog.log(
        user=user,
        action=AuditLog.Action.LOGIN,
        model_name="accounts.User",
        object_id=str(user.pk),
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    """Log user logout events."""
    if user:
        AuditLog.log(
            user=user,
            action=AuditLog.Action.LOGOUT,
            model_name="accounts.User",
            object_id=str(user.pk),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
```

### Register Signals in AppConfig

```python
# legal/apps.py

from django.apps import AppConfig


class LegalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "legal"
    verbose_name = "Rechtliches & DSGVO"

    def ready(self):
        import legal.signals  # noqa: F401
```
