# Celery Task Implementations Reference

## Overview

This reference documents all Celery task configurations and implementations for the Lebenslauf-Builder platform, including PDF generation, email sending, invoice processing, GDPR compliance tasks, sitemap regeneration, data cleanup, periodic scheduling, and Django signal handlers.

---

## 1. Celery Configuration

```python
# config/settings/celery.py

"""
Celery configuration for the Lebenslauf-Builder project.

Broker: Redis (same instance as Django cache, different DB)
Result Backend: Redis (for task result storage)
Serializer: JSON (for security - JSON only, no other serializers)
"""

from datetime import timedelta

# === Broker ===
CELERY_BROKER_URL = env("REDIS_URL", default="redis://redis:6379/1")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 43200,  # 12 hours
    "max_retries": 3,
    "interval_start": 0,
    "interval_step": 0.2,
    "interval_max": 0.5,
}

# === Result Backend ===
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/2")
CELERY_RESULT_EXPIRES = timedelta(days=1)

# === Serialization ===
# IMPORTANT: Only JSON is used for serialization. This is a security requirement.
# Never use unsafe serializers in production.
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# === Task execution ===
CELERY_TASK_ACKS_LATE = True  # Acknowledge after execution (not before)
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes soft limit
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes hard limit
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute

# === Task routing ===
CELERY_TASK_ROUTES = {
    # PDF generation is CPU-intensive -> dedicated queue
    "automation.tasks.generate_pdf": {"queue": "pdf"},
    "automation.tasks.generate_invoice_pdf": {"queue": "pdf"},

    # Email sending -> email queue (rate-limited)
    "automation.tasks.send_email": {"queue": "email"},

    # GDPR tasks -> gdpr queue (monitored, audited)
    "automation.tasks.process_gdpr_deletion": {"queue": "gdpr"},
    "automation.tasks.process_gdpr_export": {"queue": "gdpr"},

    # Default queue for everything else
    "automation.tasks.*": {"queue": "default"},
}

# === Task rate limits ===
CELERY_TASK_ANNOTATIONS = {
    "automation.tasks.send_email": {"rate_limit": "30/m"},  # Max 30 emails per minute
}

# === Monitoring ===
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# === Timezone ===
CELERY_TIMEZONE = "Europe/Berlin"
CELERY_ENABLE_UTC = True
```

---

## 2. celery.py App Setup

```python
# config/celery.py

"""
Celery application setup for the Lebenslauf-Builder project.

Autodiscovers tasks from all installed Django apps.
Used as the entry point for Celery workers:
    celery -A config worker -l info -Q default,pdf,email,gdpr
"""

import os

from celery import Celery
from celery.signals import (
    task_failure,
    task_retry,
    task_success,
    worker_ready,
)

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("lebenslauf_builder")

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in all installed apps
app.autodiscover_tasks()


# === Signal handlers for monitoring ===

@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, traceback=None, **kwargs):
    """Log task failures to Sentry and application log."""
    import logging
    import sentry_sdk

    logger = logging.getLogger("celery.tasks")
    logger.error(
        f"Task {sender.name}[{task_id}] failed: {exception}",
        exc_info=(type(exception), exception, traceback),
    )

    sentry_sdk.capture_exception(exception)


@task_retry.connect
def handle_task_retry(sender=None, request=None, reason=None, **kwargs):
    """Log task retries."""
    import logging

    logger = logging.getLogger("celery.tasks")
    logger.warning(
        f"Task {sender.name}[{request.id}] retrying: {reason}"
    )


@task_success.connect
def handle_task_success(sender=None, result=None, **kwargs):
    """Optional: track task success metrics."""
    pass


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Log when worker is ready to accept tasks."""
    import logging

    logger = logging.getLogger("celery.worker")
    logger.info("Celery worker ready and accepting tasks.")


# === Debug task ===

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery connectivity."""
    print(f"Request: {self.request!r}")
```

```python
# config/__init__.py

# Ensure Celery app is loaded when Django starts
from .celery import app as celery_app

__all__ = ("celery_app",)
```

---

## 3. generate_pdf Task

```python
# automation/tasks.py

import logging
import tempfile
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="automation.tasks.generate_pdf",
    queue="pdf",
    max_retries=2,
    soft_time_limit=120,
    time_limit=180,
    acks_late=True,
)
def generate_pdf(self, document_id: str) -> dict:
    """
    Generate a PDF from a document using WeasyPrint.

    Steps:
    1. Load the Document and its associated Template from the database
    2. Merge document content_data with template HTML
    3. Render HTML string with Django template engine
    4. Convert to PDF via WeasyPrint
    5. Save PDF to document.pdf_file field
    6. Update document status

    Args:
        document_id: UUID string of the Document

    Returns:
        dict with keys: document_id, pdf_url, file_size

    Raises:
        self.retry: On transient errors (DB connection, file I/O)
    """
    from documents.models import Document

    try:
        document = Document.objects.select_related("template", "user").get(
            pk=document_id
        )
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found, skipping PDF generation.")
        return {"error": "Document not found", "document_id": document_id}

    try:
        logger.info(f"Generating PDF for document {document_id} ({document.title})")

        # 1. Load template
        template = document.template
        if not template:
            raise ValueError(f"Document {document_id} has no template assigned.")

        # 2. Render HTML with document data
        template_html = template.html_content
        css_content = template.css_content

        # Merge content data into template context
        context = {
            "document": document,
            "data": document.content_data,  # JSONField with all user data
            "style": document.style_data,  # JSONField with styling overrides
            "template_css": css_content,
            "static_url": settings.STATIC_URL,
            "media_url": settings.MEDIA_URL,
        }

        html_string = render_to_string(
            "documents/pdf_render.html",
            context,
        )

        # 3. Generate PDF with WeasyPrint
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        font_config = FontConfiguration()

        html = HTML(string=html_string, base_url=settings.STATIC_ROOT)
        css = CSS(string=css_content, font_config=font_config)

        pdf_bytes = html.write_pdf(
            stylesheets=[css],
            font_config=font_config,
            presentational_hints=True,
        )

        # 4. Save PDF to document
        filename = f"{document.document_type}_{document.id}.pdf"
        document.pdf_file.save(
            filename,
            ContentFile(pdf_bytes),
            save=False,
        )
        document.pdf_generated_at = __import__("django.utils.timezone", fromlist=["now"]).now()
        document.save(update_fields=["pdf_file", "pdf_generated_at", "updated_at"])

        file_size = len(pdf_bytes)

        logger.info(
            f"PDF generated for document {document_id}: "
            f"{filename} ({file_size} bytes)"
        )

        return {
            "document_id": str(document_id),
            "pdf_url": document.pdf_file.url,
            "file_size": file_size,
        }

    except Exception as exc:
        logger.exception(f"PDF generation failed for document {document_id}")

        # Retry on transient errors
        try:
            self.retry(exc=exc, countdown=30 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for PDF generation: document {document_id}"
            )
            return {"error": str(exc), "document_id": document_id}
```

---

## 4. send_email Task

```python
# automation/tasks.py (continued)

@shared_task(
    bind=True,
    name="automation.tasks.send_email",
    queue="email",
    max_retries=3,
    soft_time_limit=30,
    time_limit=60,
    rate_limit="30/m",
)
def send_email(
    self,
    to_email: str,
    subject: str,
    template_name: str,
    context: dict,
    from_email: str | None = None,
    reply_to: str | None = None,
    attachments: list | None = None,
) -> dict:
    """
    Send a templated email via django-anymail (AWS SES backend).

    Args:
        to_email: Recipient email address
        subject: Email subject line
        template_name: Path to Django template (e.g., 'emails/welcome.html')
        context: Template context dictionary
        from_email: Sender email (default: DEFAULT_FROM_EMAIL)
        reply_to: Reply-to address
        attachments: List of dicts with keys: filename, content (base64), mimetype

    Returns:
        dict with keys: message_id, status
    """
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string

    try:
        # Render HTML template
        html_body = render_to_string(template_name, context)

        # Create plain text version (strip HTML)
        from django.utils.html import strip_tags
        text_body = strip_tags(html_body)

        # Build email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            reply_to=[reply_to] if reply_to else None,
        )
        email.attach_alternative(html_body, "text/html")

        # Add attachments if provided
        if attachments:
            import base64
            for attachment in attachments:
                email.attach(
                    attachment["filename"],
                    base64.b64decode(attachment["content"]),
                    attachment.get("mimetype", "application/octet-stream"),
                )

        # Send
        email.send(fail_silently=False)

        # Get message ID from anymail
        message_id = getattr(email, "anymail_status", {}).get("message_id", "unknown")

        logger.info(f"Email sent to {to_email}: {subject} (ID: {message_id})")

        return {
            "status": "sent",
            "message_id": message_id,
            "to_email": to_email,
        }

    except Exception as exc:
        logger.exception(f"Email send failed: to={to_email}, subject={subject}")

        try:
            self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for email to {to_email}")
            return {
                "status": "failed",
                "error": str(exc),
                "to_email": to_email,
            }
```

---

## 5. generate_invoice_pdf Task

```python
# automation/tasks.py (continued)

@shared_task(
    bind=True,
    name="automation.tasks.generate_invoice_pdf",
    queue="pdf",
    max_retries=2,
    soft_time_limit=60,
    time_limit=120,
)
def generate_invoice_pdf(self, invoice_id: str) -> dict:
    """
    Generate PDF for an invoice and finalize it (GoBD-compliant).

    Args:
        invoice_id: UUID string of the Invoice

    Returns:
        dict with keys: invoice_id, rechnungsnummer, pdf_url
    """
    from invoices.models import Invoice
    from invoices.services import InvoiceService

    try:
        invoice = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        logger.error(f"Invoice {invoice_id} not found.")
        return {"error": "Invoice not found", "invoice_id": invoice_id}

    if invoice.is_finalized:
        logger.warning(f"Invoice {invoice.rechnungsnummer} already finalized, skipping.")
        return {
            "invoice_id": str(invoice_id),
            "rechnungsnummer": invoice.rechnungsnummer,
            "pdf_url": invoice.pdf_file.url if invoice.pdf_file else None,
            "status": "already_finalized",
        }

    try:
        service = InvoiceService()
        invoice = service.generate_invoice_pdf(invoice)

        logger.info(f"Invoice PDF generated: {invoice.rechnungsnummer}")

        return {
            "invoice_id": str(invoice_id),
            "rechnungsnummer": invoice.rechnungsnummer,
            "pdf_url": invoice.pdf_file.url,
            "status": "generated",
        }

    except Exception as exc:
        logger.exception(f"Invoice PDF generation failed: {invoice_id}")

        try:
            self.retry(exc=exc, countdown=30 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for invoice PDF: {invoice_id}")
            return {"error": str(exc), "invoice_id": invoice_id}
```

---

## 6. process_gdpr_deletion Task

```python
# automation/tasks.py (continued)

@shared_task(
    bind=True,
    name="automation.tasks.process_gdpr_deletion",
    queue="gdpr",
    max_retries=1,
    soft_time_limit=300,
    time_limit=600,
)
def process_gdpr_deletion(self, data_request_id: str) -> dict:
    """
    Process GDPR Art. 17 data deletion request.

    Steps:
    1. Validate the request is still active (not cancelled)
    2. Soft-delete all user documents
    3. Anonymize personal data in user profile
    4. Anonymize personal data in invoices (retain financial data per GoBD)
    5. Cancel active subscriptions via Stripe
    6. Deactivate user account
    7. Create audit log entry
    8. Schedule hard deletion of soft-deleted records after 30 days
    9. Send confirmation email
    10. Mark request as completed

    GoBD Exception: Invoice financial data is retained for 10 years.
    Personal data on invoices is anonymized but financial records remain.

    Args:
        data_request_id: UUID string of the DataRequest

    Returns:
        dict with deletion summary
    """
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from django.utils import timezone

    from documents.models import Document, Bewerbungsmappe
    from gdpr.models import DataRequest, AuditLog
    from invoices.models import Invoice
    from payments.models import Subscription

    User = get_user_model()

    try:
        data_request = DataRequest.objects.select_related("user").get(
            pk=data_request_id
        )
    except DataRequest.DoesNotExist:
        logger.error(f"DataRequest {data_request_id} not found.")
        return {"error": "DataRequest not found"}

    # Check if request was cancelled during grace period
    if data_request.status == "cancelled":
        logger.info(f"DataRequest {data_request_id} was cancelled, skipping.")
        return {"status": "cancelled"}

    user = data_request.user

    try:
        data_request.status = "processing"
        data_request.save(update_fields=["status", "updated_at"])

        deletion_summary = {
            "user_id": user.id,
            "email": user.email,  # Logged before anonymization
        }

        with transaction.atomic():
            # 1. Soft-delete all documents
            docs_deleted = Document.objects.filter(
                user=user, is_deleted=False
            ).update(
                is_deleted=True,
                deleted_at=timezone.now(),
            )
            deletion_summary["documents_deleted"] = docs_deleted

            # 2. Soft-delete Bewerbungsmappen
            mappen_deleted = Bewerbungsmappe.objects.filter(
                user=user, is_deleted=False
            ).update(
                is_deleted=True,
                deleted_at=timezone.now(),
            )
            deletion_summary["mappen_deleted"] = mappen_deleted

            # 3. Anonymize user profile
            profile = user.profile
            profile.address_line1 = "GELOESCHT"
            profile.address_line2 = ""
            profile.postal_code = "00000"
            profile.city = "GELOESCHT"
            profile.phone = ""
            if profile.photo:
                profile.photo.delete(save=False)
            profile.consent_analytics = False
            profile.consent_marketing_email = False
            profile.consent_third_party = False
            profile.save()

            # 4. Anonymize invoices (GoBD: keep financial data, anonymize personal)
            invoices_anonymized = Invoice.objects.filter(customer=user).update(
                customer_name="DSGVO GELOESCHT",
                customer_email="geloescht@example.invalid",
                customer_address_line1="GELOESCHT",
                customer_address_line2="",
                customer_postal_code="00000",
                customer_city="GELOESCHT",
                # Financial data preserved per GoBD:
                # nettobetrag, mwst_betrag, bruttobetrag, rechnungsnummer, etc.
            )
            deletion_summary["invoices_anonymized"] = invoices_anonymized

            # 5. Cancel active Stripe subscriptions
            active_subs = Subscription.objects.filter(
                user=user, status__in=["active", "trialing"]
            )
            for sub in active_subs:
                try:
                    import stripe
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    stripe.Subscription.cancel(sub.stripe_subscription_id)
                    sub.status = "cancelled"
                    sub.cancelled_at = timezone.now()
                    sub.save(update_fields=["status", "cancelled_at", "updated_at"])
                except Exception as e:
                    logger.warning(f"Failed to cancel Stripe sub {sub.stripe_subscription_id}: {e}")
            deletion_summary["subscriptions_cancelled"] = active_subs.count()

            # 6. Deactivate user account
            user.is_active = False
            user.first_name = "GELOESCHT"
            user.last_name = ""
            # Anonymize email but keep unique constraint satisfaction
            user.email = f"deleted_{user.id}@example.invalid"
            user.set_unusable_password()
            user.save()

            # 7. Create audit log
            AuditLog.objects.create(
                action="gdpr_deletion",
                user_id=user.id,
                details={
                    "data_request_id": str(data_request_id),
                    "summary": deletion_summary,
                },
                ip_address=data_request.ip_address,
            )

        # 8. Schedule hard deletion of soft-deleted data (30 days)
        cleanup_expired_data.apply_async(
            args=[user.id],
            eta=timezone.now() + timezone.timedelta(days=30),
        )

        # 9. Send confirmation email to original address
        send_email.delay(
            to_email=deletion_summary["email"],
            subject="Ihre Daten wurden geloescht - Lebenslauf-Builder",
            template_name="emails/gdpr_deletion_confirmation.html",
            context={
                "request_id": str(data_request_id),
                "deletion_date": timezone.now().strftime("%d.%m.%Y"),
            },
        )

        # 10. Mark request as completed
        data_request.status = "completed"
        data_request.completed_at = timezone.now()
        data_request.save(update_fields=["status", "completed_at", "updated_at"])

        logger.info(
            f"GDPR deletion completed for user {user.id}: {deletion_summary}"
        )

        return {
            "status": "completed",
            "summary": deletion_summary,
        }

    except Exception as exc:
        logger.exception(f"GDPR deletion failed for request {data_request_id}")

        data_request.status = "failed"
        data_request.error_message = str(exc)
        data_request.save(update_fields=["status", "error_message", "updated_at"])

        # Do NOT retry automatically - admin should review
        return {"status": "failed", "error": str(exc)}
```

---

## 7. process_gdpr_export Task

```python
# automation/tasks.py (continued)

@shared_task(
    bind=True,
    name="automation.tasks.process_gdpr_export",
    queue="gdpr",
    max_retries=2,
    soft_time_limit=300,
    time_limit=600,
)
def process_gdpr_export(self, data_request_id: str) -> dict:
    """
    Process GDPR Art. 20 data portability export request.

    Compiles all user data into a ZIP archive containing:
    - user_data.json: Profile, account settings, consent history
    - documents/: All user documents as PDF files
    - invoices/: All invoice PDFs
    - activity_log.json: Login and activity history

    The ZIP is saved to a temporary file, uploaded to media storage,
    and a download link is emailed to the user (valid for 48 hours).

    Args:
        data_request_id: UUID string of the DataRequest

    Returns:
        dict with export file URL and stats
    """
    import json
    import zipfile
    from io import BytesIO

    from django.contrib.auth import get_user_model
    from django.core.files.base import ContentFile
    from django.utils import timezone

    from documents.models import Document
    from gdpr.models import DataRequest, ConsentLog, AuditLog
    from invoices.models import Invoice

    User = get_user_model()

    try:
        data_request = DataRequest.objects.select_related("user").get(
            pk=data_request_id
        )
    except DataRequest.DoesNotExist:
        logger.error(f"DataRequest {data_request_id} not found.")
        return {"error": "DataRequest not found"}

    user = data_request.user

    try:
        data_request.status = "processing"
        data_request.save(update_fields=["status", "updated_at"])

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # === 1. User data JSON ===
            profile = user.profile
            user_data = {
                "account": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "date_joined": user.date_joined.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                },
                "profile": {
                    "address_line1": profile.address_line1,
                    "address_line2": profile.address_line2,
                    "postal_code": profile.postal_code,
                    "city": profile.city,
                    "country": profile.country,
                    "phone": profile.phone,
                },
                "consent_settings": {
                    "analytics": profile.consent_analytics,
                    "marketing_email": profile.consent_marketing_email,
                    "third_party_tracking": profile.consent_third_party,
                },
                "export_generated_at": timezone.now().isoformat(),
            }
            zf.writestr(
                "user_data.json",
                json.dumps(user_data, indent=2, ensure_ascii=False),
            )

            # === 2. Consent change history ===
            consent_logs = list(
                ConsentLog.objects
                .filter(user=user)
                .order_by("created_at")
                .values("consent_type", "old_value", "new_value", "created_at", "ip_address")
            )
            for log in consent_logs:
                log["created_at"] = log["created_at"].isoformat()
            zf.writestr(
                "consent_history.json",
                json.dumps(consent_logs, indent=2, ensure_ascii=False),
            )

            # === 3. Documents as PDF ===
            documents = Document.objects.filter(user=user, is_deleted=False)
            doc_count = 0

            for doc in documents:
                if doc.pdf_file:
                    try:
                        doc.pdf_file.open("rb")
                        zf.writestr(
                            f"documents/{doc.document_type}_{doc.title[:50]}_{doc.id}.pdf",
                            doc.pdf_file.read(),
                        )
                        doc.pdf_file.close()
                        doc_count += 1
                    except Exception as e:
                        logger.warning(f"Could not include PDF for document {doc.id}: {e}")

                # Also include document content data as JSON
                doc_json = {
                    "id": str(doc.id),
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "content_data": doc.content_data,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                }
                zf.writestr(
                    f"documents/{doc.id}_data.json",
                    json.dumps(doc_json, indent=2, ensure_ascii=False),
                )

            # === 4. Invoice PDFs ===
            invoices = Invoice.objects.filter(customer=user, is_finalized=True)
            invoice_count = 0

            for invoice in invoices:
                if invoice.pdf_file:
                    try:
                        invoice.pdf_file.open("rb")
                        zf.writestr(
                            f"invoices/{invoice.rechnungsnummer}.pdf",
                            invoice.pdf_file.read(),
                        )
                        invoice.pdf_file.close()
                        invoice_count += 1
                    except Exception as e:
                        logger.warning(f"Could not include invoice {invoice.rechnungsnummer}: {e}")

            # === 5. Activity/audit log ===
            audit_logs = list(
                AuditLog.objects
                .filter(user_id=user.id)
                .order_by("created_at")
                .values("action", "details", "ip_address", "created_at")
            )
            for log in audit_logs:
                log["created_at"] = log["created_at"].isoformat()
            zf.writestr(
                "activity_log.json",
                json.dumps(audit_logs, indent=2, ensure_ascii=False),
            )

        # Save ZIP file
        zip_buffer.seek(0)
        zip_content = zip_buffer.getvalue()

        filename = f"gdpr_export_{user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        data_request.export_file.save(
            filename,
            ContentFile(zip_content),
            save=False,
        )
        data_request.status = "completed"
        data_request.completed_at = timezone.now()
        data_request.save(update_fields=[
            "export_file", "status", "completed_at", "updated_at"
        ])

        # Send download link email
        from django.urls import reverse
        download_url = reverse("gdpr:download_export", kwargs={"pk": str(data_request.id)})

        send_email.delay(
            to_email=user.email,
            subject="Ihr Datenexport ist bereit - Lebenslauf-Builder",
            template_name="emails/gdpr_export_ready.html",
            context={
                "user_name": user.get_full_name() or user.email,
                "download_url": f"{settings.SITE_URL}{download_url}",
                "expires_at": (timezone.now() + timezone.timedelta(hours=48)).strftime("%d.%m.%Y %H:%M"),
                "file_size_mb": round(len(zip_content) / (1024 * 1024), 2),
                "doc_count": doc_count,
                "invoice_count": invoice_count,
            },
        )

        logger.info(
            f"GDPR export completed for user {user.id}: "
            f"{doc_count} docs, {invoice_count} invoices, "
            f"{len(zip_content)} bytes"
        )

        return {
            "status": "completed",
            "file_size": len(zip_content),
            "doc_count": doc_count,
            "invoice_count": invoice_count,
        }

    except Exception as exc:
        logger.exception(f"GDPR export failed for request {data_request_id}")

        data_request.status = "failed"
        data_request.error_message = str(exc)
        data_request.save(update_fields=["status", "error_message", "updated_at"])

        try:
            self.retry(exc=exc, countdown=120)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "error": str(exc)}
```

---

## 8. regenerate_sitemap Task

```python
# automation/tasks.py (continued)

@shared_task(
    name="automation.tasks.regenerate_sitemap",
    soft_time_limit=60,
    time_limit=120,
)
def regenerate_sitemap() -> dict:
    """
    Regenerate the XML sitemap by calling the management command.

    Triggered by:
    - Celery beat (daily)
    - Django signal when article is published/unpublished
    - Manual admin action

    Returns:
        dict with url_count and file_path
    """
    from django.core.management import call_command
    from io import StringIO

    stdout = StringIO()

    try:
        call_command("generate_sitemap", stdout=stdout)
        output = stdout.getvalue()

        logger.info(f"Sitemap regenerated: {output.strip()}")

        return {
            "status": "completed",
            "output": output.strip(),
        }
    except Exception as exc:
        logger.exception("Sitemap regeneration failed")
        return {"status": "failed", "error": str(exc)}
```

---

## 9. cleanup_expired_data Task

```python
# automation/tasks.py (continued)

@shared_task(
    name="automation.tasks.cleanup_expired_data",
    soft_time_limit=300,
    time_limit=600,
)
def cleanup_expired_data(user_id: int | None = None) -> dict:
    """
    Hard-delete soft-deleted records that have passed the 30-day window.

    When called with user_id: Deletes only that user's soft-deleted records.
    When called without: Scans all soft-deleted records older than 30 days.

    Respects GoBD: Never deletes invoices or financial records.

    Args:
        user_id: Optional user ID to scope deletion

    Returns:
        dict with deletion counts
    """
    from django.utils import timezone
    from documents.models import Document, Bewerbungsmappe, BewerbungsmappeItem

    cutoff_date = timezone.now() - timezone.timedelta(days=30)
    summary = {}

    try:
        # === Documents ===
        doc_queryset = Document.objects.filter(
            is_deleted=True,
            deleted_at__lte=cutoff_date,
        )
        if user_id:
            doc_queryset = doc_queryset.filter(user_id=user_id)

        # Delete PDF files from storage first
        for doc in doc_queryset:
            if doc.pdf_file:
                doc.pdf_file.delete(save=False)
            if doc.thumbnail:
                doc.thumbnail.delete(save=False)

        docs_deleted, _ = doc_queryset.delete()
        summary["documents_hard_deleted"] = docs_deleted

        # === Bewerbungsmappen ===
        mappe_queryset = Bewerbungsmappe.objects.filter(
            is_deleted=True,
            deleted_at__lte=cutoff_date,
        )
        if user_id:
            mappe_queryset = mappe_queryset.filter(user_id=user_id)

        mappen_deleted, _ = mappe_queryset.delete()
        summary["mappen_hard_deleted"] = mappen_deleted

        # === Expired GDPR export files (48h) ===
        from gdpr.models import DataRequest
        export_cutoff = timezone.now() - timezone.timedelta(hours=48)
        expired_exports = DataRequest.objects.filter(
            request_type="export",
            status="completed",
            completed_at__lte=export_cutoff,
        ).exclude(export_file="")

        export_count = 0
        for export in expired_exports:
            if export.export_file:
                export.export_file.delete(save=False)
                export.export_file = ""
                export.save(update_fields=["export_file", "updated_at"])
                export_count += 1
        summary["expired_exports_cleaned"] = export_count

        logger.info(f"Cleanup completed: {summary}")

        return {
            "status": "completed",
            "summary": summary,
        }

    except Exception as exc:
        logger.exception("Data cleanup failed")
        return {"status": "failed", "error": str(exc)}
```

---

## 10. Celery Beat Schedule

```python
# config/settings/celery.py (continued)

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # === Daily tasks ===

    "regenerate-sitemap-daily": {
        "task": "automation.tasks.regenerate_sitemap",
        "schedule": crontab(hour=3, minute=0),  # 03:00 Berlin time
        "options": {"queue": "default"},
    },

    "cleanup-expired-data-daily": {
        "task": "automation.tasks.cleanup_expired_data",
        "schedule": crontab(hour=4, minute=0),  # 04:00
        "options": {"queue": "default"},
    },

    # === Weekly tasks ===

    "verify-invoice-sequence-weekly": {
        "task": "automation.tasks.verify_invoice_sequence",
        "schedule": crontab(hour=5, minute=0, day_of_week=1),  # Monday 05:00
        "options": {"queue": "default"},
    },

    "check-retention-compliance-weekly": {
        "task": "automation.tasks.check_retention_compliance",
        "schedule": crontab(hour=5, minute=30, day_of_week=1),  # Monday 05:30
        "options": {"queue": "default"},
    },

    # === Periodic monitoring ===

    "check-overdue-gdpr-requests": {
        "task": "automation.tasks.check_overdue_gdpr_requests",
        "schedule": crontab(hour=9, minute=0),  # 09:00 daily
        "options": {"queue": "gdpr"},
    },

    "send-subscription-expiry-reminders": {
        "task": "automation.tasks.send_subscription_expiry_reminders",
        "schedule": crontab(hour=10, minute=0),  # 10:00 daily
        "options": {"queue": "email"},
    },
}
```

---

## 11. Django Signals

```python
# automation/signals.py

"""
Django signal handlers that trigger Celery tasks.

Connected in automation/apps.py via ready() method.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="accounts.User")
def handle_user_created(sender, instance, created, **kwargs):
    """
    Trigger welcome email and webhook when a new user registers.

    Fired by: User.objects.create() or User.save() with created=True
    """
    if not created:
        return

    from automation.tasks import send_email

    # Send welcome email
    send_email.delay(
        to_email=instance.email,
        subject="Willkommen beim Lebenslauf-Builder!",
        template_name="emails/welcome.html",
        context={
            "user_name": instance.get_full_name() or instance.email,
            "login_url": f"{__import__('django.conf', fromlist=['settings']).settings.SITE_URL}/anmelden/",
        },
    )

    # Trigger webhook for n8n automation
    from automation.tasks import trigger_webhook
    trigger_webhook.delay(
        event_type="user.registered",
        payload={
            "user_id": instance.id,
            "email": instance.email,
            "registered_at": instance.date_joined.isoformat(),
        },
    )

    logger.info(f"New user registered: {instance.id} ({instance.email})")


@receiver(post_save, sender="documents.Document")
def handle_document_saved(sender, instance, created, **kwargs):
    """
    Trigger actions when a document is created or updated.

    On creation:
    - Trigger analytics webhook
    - Generate initial PDF if template is assigned

    On update:
    - Regenerate PDF if content changed
    """
    if created:
        # Trigger analytics webhook
        from automation.tasks import trigger_webhook
        trigger_webhook.delay(
            event_type="document.created",
            payload={
                "document_id": str(instance.id),
                "user_id": instance.user_id,
                "document_type": instance.document_type,
                "template_id": str(instance.template_id) if instance.template_id else None,
                "created_at": instance.created_at.isoformat(),
            },
        )

        logger.info(f"Document created: {instance.id} ({instance.document_type})")

    else:
        # Check if content changed (regenerate PDF)
        if instance.tracker.has_changed("content_data") and instance.template:
            from automation.tasks import generate_pdf
            generate_pdf.delay(str(instance.id))

            logger.info(f"Document updated, PDF regeneration triggered: {instance.id}")


@receiver(post_save, sender="blog.Article")
def handle_article_published(sender, instance, **kwargs):
    """Regenerate sitemap when an article is published or unpublished."""
    if instance.tracker.has_changed("status"):
        from automation.tasks import regenerate_sitemap
        regenerate_sitemap.delay()

        logger.info(
            f"Article status changed to {instance.status}, "
            f"sitemap regeneration triggered."
        )
```

```python
# automation/apps.py

from django.apps import AppConfig


class AutomationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "automation"
    verbose_name = "Automatisierung"

    def ready(self):
        # Import signals to register them
        import automation.signals  # noqa: F401
```
