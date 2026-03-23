# Dashboard Views Reference

## Overview

All dashboard views for the Lebenslauf-Builder platform. Views are organized into three tiers: User Dashboard, Account Management, and Admin Dashboard. All views use Django class-based views with HTMX partial rendering support.

---

## 1. DashboardView (Main Dashboard)

```python
# dashboard/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from documents.models import Document
from payments.models import Subscription


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard landing page.

    Displays:
    - Document count summary (total, Lebenslauf, Anschreiben, Deckblatt)
    - Recent activity feed (last 10 actions)
    - Current subscription status badge
    - Quick action buttons (new document, templates)
    - Usage stats (documents created this month, remaining in plan)

    URL: /dashboard/
    Template: dashboard/dashboard_home.html
    """

    template_name = "dashboard/dashboard_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Document counts by type
        doc_counts = (
            Document.objects
            .filter(user=user, is_deleted=False)
            .values("document_type")
            .annotate(count=Count("id"))
        )

        type_counts = {item["document_type"]: item["count"] for item in doc_counts}
        total_docs = sum(type_counts.values())

        context["document_counts"] = {
            "total": total_docs,
            "lebenslauf": type_counts.get("lebenslauf", 0),
            "anschreiben": type_counts.get("anschreiben", 0),
            "deckblatt": type_counts.get("deckblatt", 0),
        }

        # Recent activity (last 10 events)
        context["recent_activity"] = (
            Document.objects
            .filter(user=user, is_deleted=False)
            .order_by("-updated_at")[:10]
            .values("id", "title", "document_type", "updated_at")
        )

        # Current subscription
        context["subscription"] = (
            Subscription.objects
            .filter(user=user, status__in=["active", "trialing"])
            .select_related("plan")
            .first()
        )

        # Usage this month
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        context["docs_this_month"] = (
            Document.objects
            .filter(user=user, created_at__gte=current_month_start, is_deleted=False)
            .count()
        )

        # Plan limits
        subscription = context["subscription"]
        if subscription and subscription.plan:
            context["plan_doc_limit"] = subscription.plan.max_documents_per_month
        else:
            context["plan_doc_limit"] = 3  # Free tier default

        context["page_title"] = "Dashboard"
        return context
```

---

## 2. DocumentListView (HTMX Grid/List with Filters)

```python
# dashboard/views.py

from django.views.generic import ListView


class DocumentListView(LoginRequiredMixin, ListView):
    """
    Document listing view with HTMX support for:
    - Grid/List view toggle (persisted in session)
    - Filtering by document_type, template, date range
    - Sorting by title, date_created, date_updated
    - Infinite scroll pagination via HTMX

    URL: /dashboard/dokumente/
    HTMX URL: /dashboard/dokumente/?page=N (returns partial)
    Template: dashboard/meine_dokumente.html
    Partial: dashboard/partials/document_grid.html
    """

    model = Document
    template_name = "dashboard/meine_dokumente.html"
    context_object_name = "documents"
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Document.objects
            .filter(user=user, is_deleted=False)
            .select_related("template")
            .order_by("-updated_at")
        )

        # === Filters ===
        doc_type = self.request.GET.get("type")
        if doc_type and doc_type in ["lebenslauf", "anschreiben", "deckblatt"]:
            queryset = queryset.filter(document_type=doc_type)

        template_id = self.request.GET.get("template")
        if template_id:
            queryset = queryset.filter(template_id=template_id)

        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content_data__icontains=search_query)
            )

        # === Sorting ===
        sort_by = self.request.GET.get("sort", "-updated_at")
        allowed_sorts = {
            "title": "title",
            "-title": "-title",
            "created": "created_at",
            "-created": "-created_at",
            "updated": "updated_at",
            "-updated": "-updated_at",
        }
        if sort_by in allowed_sorts:
            queryset = queryset.order_by(allowed_sorts[sort_by])

        return queryset

    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.headers.get("HX-Request"):
            # Check if this is an infinite scroll request (page > 1)
            if self.request.GET.get("page"):
                return ["dashboard/partials/document_grid_items.html"]
            # Otherwise return the full grid partial (for filter/sort updates)
            return ["dashboard/partials/document_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # View mode (grid or list), stored in session
        view_mode = self.request.GET.get("view", None)
        if view_mode in ["grid", "list"]:
            self.request.session["doc_view_mode"] = view_mode
        context["view_mode"] = self.request.session.get("doc_view_mode", "grid")

        # Active filters for template rendering
        context["active_type"] = self.request.GET.get("type", "")
        context["active_sort"] = self.request.GET.get("sort", "-updated")
        context["search_query"] = self.request.GET.get("q", "")

        # Available templates for filter dropdown
        from templates.models import DocumentTemplate
        context["available_templates"] = (
            DocumentTemplate.objects
            .filter(is_active=True)
            .values("id", "name", "document_type")
            .order_by("name")
        )

        context["page_title"] = "Meine Dokumente"
        return context
```

---

## 3. DocumentCardPartialView (Single Card HTMX Partial)

```python
# dashboard/views.py

from django.http import Http404
from django.views.generic import DetailView


class DocumentCardPartialView(LoginRequiredMixin, DetailView):
    """
    HTMX partial view for a single document card.

    Used for:
    - Refreshing a single card after editing (title update, etc.)
    - Rendering a card after duplication
    - Updating card state after action (e.g., toggle favorite)

    URL: /dashboard/dokumente/<uuid:pk>/card/
    Template: dashboard/partials/document_card.html

    Returns only the card HTML fragment, not a full page.
    """

    model = Document
    template_name = "dashboard/partials/document_card.html"
    context_object_name = "document"

    def get_queryset(self):
        return Document.objects.filter(
            user=self.request.user,
            is_deleted=False,
        ).select_related("template")

    def get(self, request, *args, **kwargs):
        # Only allow HTMX requests
        if not request.headers.get("HX-Request"):
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_mode"] = self.request.session.get("doc_view_mode", "grid")
        return context
```

---

## 4. DocumentActionView (Duplicate, Delete Actions)

```python
# dashboard/views.py

import json
import logging
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View

logger = logging.getLogger(__name__)


class DocumentActionView(LoginRequiredMixin, View):
    """
    Handle document actions via HTMX POST requests.

    Supported actions:
    - duplicate: Creates a copy of the document
    - delete: Soft-deletes the document (sets is_deleted=True)
    - favorite: Toggles favorite status
    - rename: Updates document title

    URL: /dashboard/dokumente/<uuid:pk>/action/
    Method: POST
    Headers: HX-Request required
    Body: action=<action_name>

    Returns HTMX-compatible responses:
    - duplicate: Returns the new card HTML (HX-Swap: afterbegin)
    - delete: Returns empty with HX-Trigger for card removal animation
    - favorite: Returns updated card HTML
    - rename: Returns updated card HTML
    """

    def post(self, request, pk):
        if not request.headers.get("HX-Request"):
            return JsonResponse({"error": "HTMX request required"}, status=400)

        try:
            document = Document.objects.get(
                pk=pk,
                user=request.user,
                is_deleted=False,
            )
        except Document.DoesNotExist:
            return HttpResponse(status=404)

        action = request.POST.get("action")

        if action == "duplicate":
            return self._handle_duplicate(request, document)
        elif action == "delete":
            return self._handle_delete(request, document)
        elif action == "favorite":
            return self._handle_favorite(request, document)
        elif action == "rename":
            return self._handle_rename(request, document)
        else:
            return HttpResponse("Unbekannte Aktion", status=400)

    def _handle_duplicate(self, request, document):
        """Create a copy of the document."""
        from django.template.loader import render_to_string

        new_doc = Document.objects.create(
            user=request.user,
            title=f"{document.title} (Kopie)",
            document_type=document.document_type,
            template=document.template,
            content_data=document.content_data,
            style_data=document.style_data,
        )

        # Render the new card as HTMX partial
        html = render_to_string(
            "dashboard/partials/document_card.html",
            {
                "document": new_doc,
                "view_mode": request.session.get("doc_view_mode", "grid"),
            },
            request=request,
        )

        response = HttpResponse(html)
        response["HX-Trigger"] = json.dumps({
            "documentDuplicated": {
                "id": str(new_doc.id),
                "title": new_doc.title,
            }
        })
        return response

    def _handle_delete(self, request, document):
        """Soft-delete the document."""
        document.is_deleted = True
        document.deleted_at = timezone.now()
        document.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

        logger.info(f"Document {document.id} soft-deleted by user {request.user.id}")

        response = HttpResponse("")
        response["HX-Trigger"] = json.dumps({
            "documentDeleted": {
                "id": str(document.id),
                "title": document.title,
            }
        })
        return response

    def _handle_favorite(self, request, document):
        """Toggle favorite status."""
        from django.template.loader import render_to_string

        document.is_favorite = not document.is_favorite
        document.save(update_fields=["is_favorite", "updated_at"])

        html = render_to_string(
            "dashboard/partials/document_card.html",
            {
                "document": document,
                "view_mode": request.session.get("doc_view_mode", "grid"),
            },
            request=request,
        )
        return HttpResponse(html)

    def _handle_rename(self, request, document):
        """Update document title."""
        from django.template.loader import render_to_string

        new_title = request.POST.get("title", "").strip()
        if not new_title:
            return HttpResponse("Titel darf nicht leer sein.", status=400)

        if len(new_title) > 200:
            return HttpResponse("Titel zu lang (max. 200 Zeichen).", status=400)

        document.title = new_title
        document.save(update_fields=["title", "updated_at"])

        html = render_to_string(
            "dashboard/partials/document_card.html",
            {
                "document": document,
                "view_mode": request.session.get("doc_view_mode", "grid"),
            },
            request=request,
        )
        return HttpResponse(html)
```

---

## 5. KontoView (Account Settings with HTMX Inline Saves)

```python
# dashboard/views.py

from django.contrib import messages
from django.views.generic.edit import UpdateView


class KontoView(LoginRequiredMixin, TemplateView):
    """
    Account settings page with HTMX inline form saves.

    Sections:
    - Persoenliche Daten (name, email)
    - Passwort aendern
    - Profilfoto
    - Adressdaten (for invoice generation)
    - Benachrichtigungseinstellungen

    Each section submits independently via HTMX,
    providing inline feedback without full page reload.

    URL: /dashboard/konto/
    Template: dashboard/konto.html
    """

    template_name = "dashboard/konto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["profile_form"] = ProfileForm(instance=user.profile)
        context["password_form"] = PasswordChangeForm(user=user)
        context["address_form"] = AddressForm(instance=user.profile)
        context["notification_form"] = NotificationSettingsForm(instance=user.profile)

        context["page_title"] = "Konto"
        return context


class KontoProfileUpdateView(LoginRequiredMixin, View):
    """
    HTMX endpoint for updating profile data inline.

    URL: /dashboard/konto/profil/
    Method: POST (HTMX)
    Returns: Updated form section with success/error feedback
    """

    def post(self, request):
        from django.template.loader import render_to_string

        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()
            html = render_to_string(
                "dashboard/partials/konto_profile_form.html",
                {"profile_form": form, "success_message": "Profil aktualisiert."},
                request=request,
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "profileUpdated"
            return response
        else:
            html = render_to_string(
                "dashboard/partials/konto_profile_form.html",
                {"profile_form": form},
                request=request,
            )
            return HttpResponse(html)


class KontoPasswordUpdateView(LoginRequiredMixin, View):
    """
    HTMX endpoint for password change.

    URL: /dashboard/konto/passwort/
    Method: POST (HTMX)
    """

    def post(self, request):
        from django.contrib.auth import update_session_auth_hash
        from django.template.loader import render_to_string

        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            # Keep user logged in after password change
            update_session_auth_hash(request, request.user)

            html = render_to_string(
                "dashboard/partials/konto_password_form.html",
                {
                    "password_form": PasswordChangeForm(user=request.user),
                    "success_message": "Passwort geaendert.",
                },
                request=request,
            )
            return HttpResponse(html)
        else:
            html = render_to_string(
                "dashboard/partials/konto_password_form.html",
                {"password_form": form},
                request=request,
            )
            return HttpResponse(html)


class KontoAddressUpdateView(LoginRequiredMixin, View):
    """
    HTMX endpoint for address data (used on invoices).

    URL: /dashboard/konto/adresse/
    Method: POST (HTMX)
    """

    def post(self, request):
        from django.template.loader import render_to_string

        form = AddressForm(request.POST, instance=request.user.profile)

        if form.is_valid():
            form.save()
            html = render_to_string(
                "dashboard/partials/konto_address_form.html",
                {"address_form": form, "success_message": "Adresse aktualisiert."},
                request=request,
            )
            return HttpResponse(html)
        else:
            html = render_to_string(
                "dashboard/partials/konto_address_form.html",
                {"address_form": form},
                request=request,
            )
            return HttpResponse(html)


class KontoNotificationUpdateView(LoginRequiredMixin, View):
    """
    HTMX endpoint for notification preferences.

    URL: /dashboard/konto/benachrichtigungen/
    Method: POST (HTMX)
    """

    def post(self, request):
        from django.template.loader import render_to_string

        form = NotificationSettingsForm(request.POST, instance=request.user.profile)

        if form.is_valid():
            form.save()
            html = render_to_string(
                "dashboard/partials/konto_notification_form.html",
                {
                    "notification_form": form,
                    "success_message": "Einstellungen gespeichert.",
                },
                request=request,
            )
            return HttpResponse(html)
        else:
            html = render_to_string(
                "dashboard/partials/konto_notification_form.html",
                {"notification_form": form},
                request=request,
            )
            return HttpResponse(html)
```

---

## 6. AboZahlungView (Subscription & Payment History)

```python
# dashboard/views.py

class AboZahlungView(LoginRequiredMixin, TemplateView):
    """
    Subscription status and payment history page.

    Displays:
    - Current plan card (name, price, features, renewal date)
    - Plan upgrade/downgrade buttons
    - Payment history table with invoice download links
    - Payment method on file (last 4 digits)
    - Cancel subscription option (with Widerruf notice)

    URL: /dashboard/abo-zahlung/
    Template: dashboard/abo_zahlung.html
    """

    template_name = "dashboard/abo_zahlung.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Current subscription
        subscription = (
            Subscription.objects
            .filter(user=user, status__in=["active", "trialing", "past_due"])
            .select_related("plan")
            .first()
        )
        context["subscription"] = subscription

        # Available plans for upgrade/downgrade
        from payments.models import Plan
        context["available_plans"] = (
            Plan.objects
            .filter(is_active=True)
            .order_by("price_monthly")
        )

        # Payment history (last 24 months)
        from invoices.models import Invoice
        context["invoices"] = (
            Invoice.objects
            .filter(customer=user, is_finalized=True)
            .order_by("-rechnungsdatum")[:50]
        )

        # Payment method on file
        if subscription and subscription.stripe_customer_id:
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY

            try:
                customer = stripe.Customer.retrieve(
                    subscription.stripe_customer_id,
                    expand=["default_source", "invoice_settings.default_payment_method"],
                )
                pm = customer.invoice_settings.default_payment_method
                if pm:
                    context["payment_method"] = {
                        "brand": pm.card.brand.title() if pm.card else "Unbekannt",
                        "last4": pm.card.last4 if pm.card else "****",
                        "exp_month": pm.card.exp_month if pm.card else "",
                        "exp_year": pm.card.exp_year if pm.card else "",
                        "type": "card",
                    }
                elif pm and hasattr(pm, "sepa_debit"):
                    context["payment_method"] = {
                        "brand": "SEPA",
                        "last4": pm.sepa_debit.last4,
                        "type": "sepa_debit",
                    }
            except Exception:
                context["payment_method"] = None

        # Widerruf eligibility
        if subscription:
            from datetime import timedelta
            days_since_start = (
                timezone.now().date() - subscription.current_period_start
            ).days
            context["widerruf_eligible"] = days_since_start <= 14
            context["widerruf_days_remaining"] = max(0, 14 - days_since_start)

        context["page_title"] = "Abo & Zahlung"
        return context


class AboUpgradeView(LoginRequiredMixin, View):
    """
    HTMX endpoint for plan upgrade/downgrade.

    URL: /dashboard/abo-zahlung/upgrade/
    Method: POST
    Body: plan_id=<uuid>

    Creates a Stripe Checkout session for the new plan
    and returns a redirect URL.
    """

    def post(self, request):
        plan_id = request.POST.get("plan_id")
        if not plan_id:
            return HttpResponse("Plan nicht angegeben.", status=400)

        from payments.models import Plan
        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return HttpResponse("Plan nicht gefunden.", status=404)

        # Create Stripe Checkout session
        from payments.services import StripeService
        service = StripeService()
        session = service.create_checkout_session(
            user=request.user,
            plan=plan,
            success_url=request.build_absolute_uri("/dashboard/abo-zahlung/?upgraded=1"),
            cancel_url=request.build_absolute_uri("/dashboard/abo-zahlung/"),
        )

        response = HttpResponse()
        response["HX-Redirect"] = session.url
        return response


class AboCancelView(LoginRequiredMixin, View):
    """
    HTMX endpoint for subscription cancellation.

    URL: /dashboard/abo-zahlung/kuendigen/
    Method: POST

    Cancels at end of current billing period (not immediately).
    """

    def post(self, request):
        from django.template.loader import render_to_string

        subscription = (
            Subscription.objects
            .filter(user=request.user, status="active")
            .first()
        )

        if not subscription:
            return HttpResponse("Kein aktives Abo gefunden.", status=404)

        import stripe
        from django.conf import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Cancel at period end (not immediate)
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
        )

        subscription.cancel_at_period_end = True
        subscription.save(update_fields=["cancel_at_period_end", "updated_at"])

        html = render_to_string(
            "dashboard/partials/abo_status_card.html",
            {"subscription": subscription, "cancel_confirmed": True},
            request=request,
        )
        return HttpResponse(html)
```

---

## 7. DatenschutzSettingsView (DSGVO Controls)

```python
# dashboard/views.py

class DatenschutzSettingsView(LoginRequiredMixin, TemplateView):
    """
    DSGVO (GDPR) privacy settings and controls.

    User rights implemented:
    - Art. 15 DSGVO: Auskunftsrecht (right of access) - data export
    - Art. 17 DSGVO: Recht auf Loeschung (right to erasure) - account deletion
    - Art. 20 DSGVO: Recht auf Datenportabilitaet (data portability) - export
    - Art. 7 Abs. 3 DSGVO: Widerruf der Einwilligung (withdraw consent)

    URL: /dashboard/datenschutz/
    Template: dashboard/datenschutz_settings.html
    """

    template_name = "dashboard/datenschutz_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile

        # Current consent settings
        context["consent_settings"] = {
            "analytics": profile.consent_analytics,
            "marketing_email": profile.consent_marketing_email,
            "third_party_tracking": profile.consent_third_party,
        }

        # Pending data requests
        from gdpr.models import DataRequest
        context["pending_requests"] = (
            DataRequest.objects
            .filter(user=user, status__in=["pending", "processing"])
            .order_by("-created_at")
        )

        # Completed data exports (available for download for 48h)
        context["available_exports"] = (
            DataRequest.objects
            .filter(
                user=user,
                request_type="export",
                status="completed",
                completed_at__gte=timezone.now() - timezone.timedelta(hours=48),
            )
            .order_by("-completed_at")
        )

        context["page_title"] = "Datenschutz"
        return context


class DatenschutzConsentUpdateView(LoginRequiredMixin, View):
    """
    HTMX endpoint for updating consent toggles.

    URL: /dashboard/datenschutz/einwilligung/
    Method: POST (HTMX)
    Body: consent_type=<type>&value=<true|false>

    Each toggle is saved independently with audit trail.
    """

    def post(self, request):
        from django.template.loader import render_to_string
        from gdpr.models import ConsentLog

        consent_type = request.POST.get("consent_type")
        value = request.POST.get("value") == "true"

        allowed_types = {
            "analytics": "consent_analytics",
            "marketing_email": "consent_marketing_email",
            "third_party": "consent_third_party",
        }

        if consent_type not in allowed_types:
            return HttpResponse("Ungueltiger Einwilligungstyp.", status=400)

        profile = request.user.profile
        field_name = allowed_types[consent_type]
        old_value = getattr(profile, field_name)

        # Update consent
        setattr(profile, field_name, value)
        profile.save(update_fields=[field_name, "updated_at"])

        # Audit log (DSGVO requires proof of consent changes)
        ConsentLog.objects.create(
            user=request.user,
            consent_type=consent_type,
            old_value=old_value,
            new_value=value,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        html = render_to_string(
            "dashboard/partials/consent_toggle.html",
            {
                "consent_type": consent_type,
                "value": value,
                "label": self._get_label(consent_type),
                "success": True,
            },
            request=request,
        )
        return HttpResponse(html)

    def _get_label(self, consent_type):
        labels = {
            "analytics": "Nutzungsanalyse",
            "marketing_email": "Marketing-E-Mails",
            "third_party": "Drittanbieter-Tracking",
        }
        return labels.get(consent_type, consent_type)


class DatenschutzDataExportView(LoginRequiredMixin, View):
    """
    HTMX endpoint to request DSGVO data export (Art. 20).

    URL: /dashboard/datenschutz/export/
    Method: POST (HTMX)

    Creates a DataRequest and triggers async Celery task.
    User receives email with download link when ready.
    """

    def post(self, request):
        from gdpr.models import DataRequest

        # Check for existing pending request
        pending = DataRequest.objects.filter(
            user=request.user,
            request_type="export",
            status__in=["pending", "processing"],
        ).exists()

        if pending:
            return HttpResponse(
                '<div class="alert alert-warning">'
                "Es laeuft bereits ein Datenexport. "
                "Bitte warten Sie, bis dieser abgeschlossen ist."
                "</div>"
            )

        # Create export request
        data_request = DataRequest.objects.create(
            user=request.user,
            request_type="export",
            status="pending",
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        # Trigger async Celery task
        from automation.tasks import process_gdpr_export
        process_gdpr_export.delay(str(data_request.id))

        return HttpResponse(
            '<div class="alert alert-success">'
            "Ihr Datenexport wird vorbereitet. "
            "Sie erhalten eine E-Mail mit dem Download-Link."
            "</div>"
        )


class DatenschutzDataDeletionView(LoginRequiredMixin, View):
    """
    HTMX endpoint to request account and data deletion (Art. 17).

    URL: /dashboard/datenschutz/loeschung/
    Method: POST (HTMX)
    Body: confirmation=DELETE

    Requires explicit confirmation text. Creates DataRequest
    and schedules async deletion after 14-day grace period.
    """

    def post(self, request):
        from gdpr.models import DataRequest

        confirmation = request.POST.get("confirmation", "")

        if confirmation != "LOESCHEN":
            return HttpResponse(
                '<div class="alert alert-danger">'
                'Bitte geben Sie "LOESCHEN" ein, um die Loeschung zu bestaetigen.'
                "</div>",
                status=400,
            )

        # Check for existing pending deletion
        pending = DataRequest.objects.filter(
            user=request.user,
            request_type="deletion",
            status__in=["pending", "processing"],
        ).exists()

        if pending:
            return HttpResponse(
                '<div class="alert alert-warning">'
                "Es laeuft bereits ein Loeschantrag."
                "</div>"
            )

        # Create deletion request (14-day grace period)
        data_request = DataRequest.objects.create(
            user=request.user,
            request_type="deletion",
            status="pending",
            ip_address=request.META.get("REMOTE_ADDR"),
            scheduled_for=timezone.now() + timezone.timedelta(days=14),
        )

        # Trigger async Celery task
        from automation.tasks import process_gdpr_deletion
        process_gdpr_deletion.apply_async(
            args=[str(data_request.id)],
            eta=data_request.scheduled_for,
        )

        return HttpResponse(
            '<div class="alert alert-info">'
            "Ihr Loeschantrag wurde registriert. "
            "Die Loeschung wird in 14 Tagen durchgefuehrt. "
            "Sie koennen den Antrag bis dahin widerrufen."
            "</div>"
        )
```

---

## 8. BewerbungsmappeView (Drag & Drop Document Ordering)

```python
# dashboard/views.py

class BewerbungsmappeView(LoginRequiredMixin, TemplateView):
    """
    Bewerbungsmappe (application portfolio) with drag & drop ordering.

    Allows users to:
    - Create named Bewerbungsmappen for different job applications
    - Add/remove documents to/from a Mappe
    - Reorder documents via drag & drop (Sortable.js)
    - Generate a combined PDF of all documents in order
    - Share via direct link or download

    URL: /dashboard/bewerbungsmappe/
    URL: /dashboard/bewerbungsmappe/<uuid:pk>/
    Template: dashboard/bewerbungsmappe.html
    """

    template_name = "dashboard/bewerbungsmappe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # All user's Bewerbungsmappen
        from documents.models import Bewerbungsmappe
        context["mappen"] = (
            Bewerbungsmappe.objects
            .filter(user=user, is_deleted=False)
            .prefetch_related("items__document")
            .order_by("-updated_at")
        )

        # Selected Mappe (if viewing specific one)
        mappe_id = self.kwargs.get("pk")
        if mappe_id:
            context["active_mappe"] = (
                Bewerbungsmappe.objects
                .filter(pk=mappe_id, user=user, is_deleted=False)
                .prefetch_related("items__document__template")
                .first()
            )

        # Available documents to add
        context["available_documents"] = (
            Document.objects
            .filter(user=user, is_deleted=False)
            .select_related("template")
            .order_by("document_type", "title")
        )

        context["page_title"] = "Bewerbungsmappe"
        return context


class BewerbungsmappeReorderView(LoginRequiredMixin, View):
    """
    HTMX endpoint for reordering documents in a Bewerbungsmappe.

    URL: /dashboard/bewerbungsmappe/<uuid:pk>/reorder/
    Method: POST (HTMX)
    Body: order[]=<item_id>&order[]=<item_id>&...

    Called by Sortable.js onEnd event.
    """

    def post(self, request, pk):
        from documents.models import Bewerbungsmappe, BewerbungsmappeItem

        try:
            mappe = Bewerbungsmappe.objects.get(
                pk=pk, user=request.user, is_deleted=False
            )
        except Bewerbungsmappe.DoesNotExist:
            return HttpResponse(status=404)

        order = request.POST.getlist("order[]")

        if not order:
            return HttpResponse(status=400)

        # Update ordering using bulk_update for efficiency
        items_to_update = []
        for position, item_id in enumerate(order, start=1):
            try:
                item = BewerbungsmappeItem.objects.get(
                    pk=item_id, mappe=mappe
                )
                item.position = position
                items_to_update.append(item)
            except BewerbungsmappeItem.DoesNotExist:
                continue

        BewerbungsmappeItem.objects.bulk_update(items_to_update, ["position"])

        response = HttpResponse("")
        response["HX-Trigger"] = json.dumps({
            "mappeReordered": {"mappe_id": str(pk)}
        })
        return response


class BewerbungsmappeAddDocumentView(LoginRequiredMixin, View):
    """
    HTMX endpoint for adding a document to a Bewerbungsmappe.

    URL: /dashboard/bewerbungsmappe/<uuid:pk>/add/
    Method: POST (HTMX)
    Body: document_id=<uuid>
    """

    def post(self, request, pk):
        from django.template.loader import render_to_string
        from documents.models import Bewerbungsmappe, BewerbungsmappeItem

        try:
            mappe = Bewerbungsmappe.objects.get(
                pk=pk, user=request.user, is_deleted=False
            )
        except Bewerbungsmappe.DoesNotExist:
            return HttpResponse(status=404)

        doc_id = request.POST.get("document_id")
        try:
            document = Document.objects.get(
                pk=doc_id, user=request.user, is_deleted=False
            )
        except Document.DoesNotExist:
            return HttpResponse("Dokument nicht gefunden.", status=404)

        # Check if already in mappe
        if BewerbungsmappeItem.objects.filter(mappe=mappe, document=document).exists():
            return HttpResponse("Dokument bereits in der Mappe.", status=400)

        # Add at end
        max_pos = (
            BewerbungsmappeItem.objects
            .filter(mappe=mappe)
            .aggregate(models.Max("position"))["position__max"]
        ) or 0

        item = BewerbungsmappeItem.objects.create(
            mappe=mappe,
            document=document,
            position=max_pos + 1,
        )

        html = render_to_string(
            "dashboard/partials/bewerbungsmappe_item.html",
            {"item": item},
            request=request,
        )
        return HttpResponse(html)
```

---

## 9. AdminDashboardView (Revenue Metrics with Chart.js)

```python
# dashboard/views.py

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


@method_decorator(staff_member_required, name="dispatch")
class AdminDashboardView(TemplateView):
    """
    Admin dashboard with revenue metrics and platform analytics.

    Displays:
    - Revenue charts (MRR, ARR, daily revenue) via Chart.js
    - User growth (registrations per day/week/month)
    - Document creation stats
    - Active subscriptions by plan
    - Churn rate
    - GDPR request queue status

    URL: /admin-dashboard/
    Template: dashboard/admin_dashboard.html
    """

    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from django.contrib.auth import get_user_model
        from payments.models import Payment, Subscription, Plan
        from invoices.models import Invoice
        from gdpr.models import DataRequest
        from datetime import timedelta

        User = get_user_model()
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        twelve_months_ago = now - timedelta(days=365)

        # === Revenue Metrics ===

        # Monthly Recurring Revenue (MRR)
        active_subs = Subscription.objects.filter(status="active").select_related("plan")
        mrr = sum(
            sub.plan.price_monthly for sub in active_subs
            if sub.plan and sub.plan.price_monthly
        )
        context["mrr"] = mrr
        context["arr"] = mrr * 12

        # Daily revenue for last 30 days (Chart.js data)
        from django.db.models.functions import TruncDate
        daily_revenue = (
            Payment.objects
            .filter(
                status="succeeded",
                created_at__gte=thirty_days_ago,
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total=models.Sum("amount_total"))
            .order_by("date")
        )

        context["revenue_chart_labels"] = json.dumps([
            item["date"].strftime("%d.%m") for item in daily_revenue
        ])
        context["revenue_chart_data"] = json.dumps([
            float(item["total"]) for item in daily_revenue
        ])

        # Monthly revenue for last 12 months
        from django.db.models.functions import TruncMonth
        monthly_revenue = (
            Payment.objects
            .filter(
                status="succeeded",
                created_at__gte=twelve_months_ago,
            )
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=models.Sum("amount_total"))
            .order_by("month")
        )

        context["monthly_revenue_labels"] = json.dumps([
            item["month"].strftime("%b %Y") for item in monthly_revenue
        ])
        context["monthly_revenue_data"] = json.dumps([
            float(item["total"]) for item in monthly_revenue
        ])

        # === User Metrics ===

        context["total_users"] = User.objects.filter(is_active=True).count()
        context["new_users_30d"] = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()

        # User registrations per day (last 30 days)
        daily_registrations = (
            User.objects
            .filter(date_joined__gte=thirty_days_ago)
            .annotate(date=TruncDate("date_joined"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        context["registrations_chart_labels"] = json.dumps([
            item["date"].strftime("%d.%m") for item in daily_registrations
        ])
        context["registrations_chart_data"] = json.dumps([
            item["count"] for item in daily_registrations
        ])

        # === Subscription Metrics ===

        context["active_subscriptions"] = Subscription.objects.filter(
            status="active"
        ).count()

        # Subscriptions by plan
        subs_by_plan = (
            Subscription.objects
            .filter(status="active")
            .values("plan__display_name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        context["subs_by_plan_labels"] = json.dumps([
            item["plan__display_name"] for item in subs_by_plan
        ])
        context["subs_by_plan_data"] = json.dumps([
            item["count"] for item in subs_by_plan
        ])

        # Churn rate (cancellations in last 30 days / active at start)
        cancellations_30d = Subscription.objects.filter(
            status="cancelled",
            cancelled_at__gte=thirty_days_ago,
        ).count()
        total_at_start = context["active_subscriptions"] + cancellations_30d
        context["churn_rate"] = (
            round(cancellations_30d / total_at_start * 100, 1)
            if total_at_start > 0 else 0
        )

        # === Document Metrics ===

        context["total_documents"] = Document.objects.filter(is_deleted=False).count()
        context["docs_created_30d"] = Document.objects.filter(
            created_at__gte=thirty_days_ago, is_deleted=False
        ).count()

        # === GDPR Request Queue ===

        context["pending_gdpr_requests"] = DataRequest.objects.filter(
            status__in=["pending", "processing"]
        ).count()

        context["page_title"] = "Admin Dashboard"
        return context
```

---

## 10. AdminUserManagementView (User List with Search/Filter)

```python
# dashboard/views.py

@method_decorator(staff_member_required, name="dispatch")
class AdminUserManagementView(ListView):
    """
    Admin user management with search, filter, and HTMX.

    Features:
    - Search by name, email
    - Filter by subscription plan, status, date range
    - Inline user actions (activate/deactivate, reset password email)
    - HTMX-powered table with pagination

    URL: /admin-dashboard/benutzer/
    Template: dashboard/admin_user_management.html
    """

    template_name = "dashboard/admin_user_management.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        queryset = (
            User.objects
            .select_related("profile")
            .prefetch_related("subscriptions__plan")
            .annotate(
                document_count=Count("documents", filter=Q(documents__is_deleted=False)),
            )
            .order_by("-date_joined")
        )

        # Search
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        # Filter by subscription status
        sub_status = self.request.GET.get("sub_status")
        if sub_status == "active":
            queryset = queryset.filter(subscriptions__status="active")
        elif sub_status == "none":
            queryset = queryset.exclude(subscriptions__status="active")
        elif sub_status == "cancelled":
            queryset = queryset.filter(subscriptions__status="cancelled")

        # Filter by plan
        plan_id = self.request.GET.get("plan")
        if plan_id:
            queryset = queryset.filter(
                subscriptions__plan_id=plan_id,
                subscriptions__status="active",
            )

        # Filter by active/inactive
        is_active = self.request.GET.get("is_active")
        if is_active == "true":
            queryset = queryset.filter(is_active=True)
        elif is_active == "false":
            queryset = queryset.filter(is_active=False)

        # Date range
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        if date_from:
            queryset = queryset.filter(date_joined__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_joined__date__lte=date_to)

        return queryset.distinct()

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["dashboard/partials/admin_user_table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from payments.models import Plan
        context["plans"] = Plan.objects.filter(is_active=True).order_by("price_monthly")

        context["search_query"] = self.request.GET.get("q", "")
        context["active_sub_status"] = self.request.GET.get("sub_status", "")
        context["active_plan"] = self.request.GET.get("plan", "")

        context["page_title"] = "Benutzerverwaltung"
        return context


@method_decorator(staff_member_required, name="dispatch")
class AdminUserActionView(View):
    """
    Admin actions on individual users.

    URL: /admin-dashboard/benutzer/<int:user_id>/action/
    Method: POST
    Body: action=<activate|deactivate|send_password_reset>
    """

    def post(self, request, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return HttpResponse(status=404)

        action = request.POST.get("action")

        if action == "activate":
            user.is_active = True
            user.save(update_fields=["is_active"])
            return HttpResponse(
                '<span class="badge bg-success">Aktiv</span>'
            )

        elif action == "deactivate":
            user.is_active = False
            user.save(update_fields=["is_active"])
            return HttpResponse(
                '<span class="badge bg-danger">Inaktiv</span>'
            )

        elif action == "send_password_reset":
            from django.contrib.auth.forms import PasswordResetForm
            form = PasswordResetForm(data={"email": user.email})
            if form.is_valid():
                form.save(request=request)
            return HttpResponse(
                '<span class="text-success">E-Mail gesendet</span>'
            )

        return HttpResponse("Unbekannte Aktion.", status=400)
```

---

## 11. AdminGDPRPanelView (Pending Requests, Audit Log)

```python
# dashboard/views.py

@method_decorator(staff_member_required, name="dispatch")
class AdminGDPRPanelView(TemplateView):
    """
    Admin GDPR management panel.

    Features:
    - Pending data export requests queue
    - Pending deletion requests queue
    - Consent change audit log
    - Manual request processing controls
    - Statistics on request types and response times

    URL: /admin-dashboard/datenschutz/
    Template: dashboard/admin_gdpr_panel.html
    """

    template_name = "dashboard/admin_gdpr_panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from gdpr.models import DataRequest, ConsentLog
        from datetime import timedelta

        now = timezone.now()

        # Pending requests
        context["pending_exports"] = (
            DataRequest.objects
            .filter(request_type="export", status="pending")
            .select_related("user")
            .order_by("created_at")
        )

        context["pending_deletions"] = (
            DataRequest.objects
            .filter(request_type="deletion", status="pending")
            .select_related("user")
            .order_by("created_at")
        )

        context["processing_requests"] = (
            DataRequest.objects
            .filter(status="processing")
            .select_related("user")
            .order_by("created_at")
        )

        # Completed requests (last 30 days)
        context["completed_requests"] = (
            DataRequest.objects
            .filter(
                status="completed",
                completed_at__gte=now - timedelta(days=30),
            )
            .select_related("user")
            .order_by("-completed_at")[:50]
        )

        # Failed requests
        context["failed_requests"] = (
            DataRequest.objects
            .filter(status="failed")
            .select_related("user")
            .order_by("-created_at")[:20]
        )

        # Recent consent changes (audit log)
        context["recent_consent_changes"] = (
            ConsentLog.objects
            .select_related("user")
            .order_by("-created_at")[:100]
        )

        # Statistics
        context["stats"] = {
            "total_exports": DataRequest.objects.filter(
                request_type="export"
            ).count(),
            "total_deletions": DataRequest.objects.filter(
                request_type="deletion"
            ).count(),
            "avg_export_time": self._calculate_avg_processing_time("export"),
            "avg_deletion_time": self._calculate_avg_processing_time("deletion"),
            "pending_count": DataRequest.objects.filter(
                status="pending"
            ).count(),
        }

        # DSGVO compliance deadline warnings
        # Art. 12 DSGVO requires response within 1 month
        one_month_ago = now - timedelta(days=30)
        context["overdue_requests"] = (
            DataRequest.objects
            .filter(
                status__in=["pending", "processing"],
                created_at__lt=one_month_ago,
            )
            .select_related("user")
            .order_by("created_at")
        )

        context["page_title"] = "DSGVO-Verwaltung"
        return context

    def _calculate_avg_processing_time(self, request_type):
        """Calculate average processing time for completed requests."""
        from django.db.models import Avg, F
        result = (
            DataRequest.objects
            .filter(
                request_type=request_type,
                status="completed",
                completed_at__isnull=False,
            )
            .aggregate(
                avg_time=Avg(F("completed_at") - F("created_at"))
            )
        )
        return result["avg_time"]


@method_decorator(staff_member_required, name="dispatch")
class AdminGDPRRequestActionView(View):
    """
    Admin actions on GDPR requests.

    URL: /admin-dashboard/datenschutz/<uuid:pk>/action/
    Method: POST (HTMX)
    Body: action=<process|cancel|retry>
    """

    def post(self, request, pk):
        from django.template.loader import render_to_string
        from gdpr.models import DataRequest

        try:
            data_request = DataRequest.objects.get(pk=pk)
        except DataRequest.DoesNotExist:
            return HttpResponse(status=404)

        action = request.POST.get("action")

        if action == "process":
            # Manually trigger processing
            data_request.status = "processing"
            data_request.save(update_fields=["status", "updated_at"])

            if data_request.request_type == "export":
                from automation.tasks import process_gdpr_export
                process_gdpr_export.delay(str(data_request.id))
            elif data_request.request_type == "deletion":
                from automation.tasks import process_gdpr_deletion
                process_gdpr_deletion.delay(str(data_request.id))

            msg = "Verarbeitung gestartet."

        elif action == "cancel":
            data_request.status = "cancelled"
            data_request.save(update_fields=["status", "updated_at"])
            msg = "Antrag storniert."

        elif action == "retry":
            if data_request.status == "failed":
                data_request.status = "pending"
                data_request.error_message = ""
                data_request.save(update_fields=["status", "error_message", "updated_at"])
                msg = "Antrag zurueckgesetzt."
            else:
                return HttpResponse("Nur fehlgeschlagene Antraege.", status=400)

        else:
            return HttpResponse("Unbekannte Aktion.", status=400)

        html = render_to_string(
            "dashboard/partials/gdpr_request_row.html",
            {"data_request": data_request, "action_message": msg},
            request=request,
        )
        return HttpResponse(html)
```

---

## URL Configuration

```python
# dashboard/urls.py

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # === User Dashboard ===
    path(
        "",
        views.DashboardView.as_view(),
        name="home",
    ),
    path(
        "dokumente/",
        views.DocumentListView.as_view(),
        name="document_list",
    ),
    path(
        "dokumente/<uuid:pk>/card/",
        views.DocumentCardPartialView.as_view(),
        name="document_card",
    ),
    path(
        "dokumente/<uuid:pk>/action/",
        views.DocumentActionView.as_view(),
        name="document_action",
    ),

    # === Account (Konto) ===
    path(
        "konto/",
        views.KontoView.as_view(),
        name="konto",
    ),
    path(
        "konto/profil/",
        views.KontoProfileUpdateView.as_view(),
        name="konto_profile",
    ),
    path(
        "konto/passwort/",
        views.KontoPasswordUpdateView.as_view(),
        name="konto_password",
    ),
    path(
        "konto/adresse/",
        views.KontoAddressUpdateView.as_view(),
        name="konto_address",
    ),
    path(
        "konto/benachrichtigungen/",
        views.KontoNotificationUpdateView.as_view(),
        name="konto_notifications",
    ),

    # === Subscription & Payment ===
    path(
        "abo-zahlung/",
        views.AboZahlungView.as_view(),
        name="abo_zahlung",
    ),
    path(
        "abo-zahlung/upgrade/",
        views.AboUpgradeView.as_view(),
        name="abo_upgrade",
    ),
    path(
        "abo-zahlung/kuendigen/",
        views.AboCancelView.as_view(),
        name="abo_cancel",
    ),

    # === Datenschutz (DSGVO) ===
    path(
        "datenschutz/",
        views.DatenschutzSettingsView.as_view(),
        name="datenschutz",
    ),
    path(
        "datenschutz/einwilligung/",
        views.DatenschutzConsentUpdateView.as_view(),
        name="datenschutz_consent",
    ),
    path(
        "datenschutz/export/",
        views.DatenschutzDataExportView.as_view(),
        name="datenschutz_export",
    ),
    path(
        "datenschutz/loeschung/",
        views.DatenschutzDataDeletionView.as_view(),
        name="datenschutz_deletion",
    ),

    # === Bewerbungsmappe ===
    path(
        "bewerbungsmappe/",
        views.BewerbungsmappeView.as_view(),
        name="bewerbungsmappe",
    ),
    path(
        "bewerbungsmappe/<uuid:pk>/",
        views.BewerbungsmappeView.as_view(),
        name="bewerbungsmappe_detail",
    ),
    path(
        "bewerbungsmappe/<uuid:pk>/reorder/",
        views.BewerbungsmappeReorderView.as_view(),
        name="bewerbungsmappe_reorder",
    ),
    path(
        "bewerbungsmappe/<uuid:pk>/add/",
        views.BewerbungsmappeAddDocumentView.as_view(),
        name="bewerbungsmappe_add",
    ),

    # === Admin Dashboard ===
    path(
        "admin-dashboard/",
        views.AdminDashboardView.as_view(),
        name="admin_dashboard",
    ),
    path(
        "admin-dashboard/benutzer/",
        views.AdminUserManagementView.as_view(),
        name="admin_users",
    ),
    path(
        "admin-dashboard/benutzer/<int:user_id>/action/",
        views.AdminUserActionView.as_view(),
        name="admin_user_action",
    ),
    path(
        "admin-dashboard/datenschutz/",
        views.AdminGDPRPanelView.as_view(),
        name="admin_gdpr",
    ),
    path(
        "admin-dashboard/datenschutz/<uuid:pk>/action/",
        views.AdminGDPRRequestActionView.as_view(),
        name="admin_gdpr_action",
    ),
]
```
