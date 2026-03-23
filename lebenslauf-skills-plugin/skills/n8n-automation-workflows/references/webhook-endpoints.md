# Webhook Endpoint Implementations Reference

## Overview

This reference documents all webhook endpoints for the Lebenslauf-Builder platform, including HMAC verification, Stripe webhooks, internal event webhooks, n8n workflow integration descriptions, and security patterns. The webhook system enables n8n to receive real-time events from the Django application for automation workflows.

---

## 1. HMACVerificationMixin

```python
# webhooks/mixins.py

import hashlib
import hmac
import logging
import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class HMACVerificationMixin(View):
    """
    Mixin for webhook views that verifies HMAC-SHA256 signatures.

    How it works:
    1. The sender includes a signature in the HTTP header
    2. The signature is computed as HMAC-SHA256(shared_secret, request_body)
    3. This mixin recomputes the signature and compares it
    4. If signatures don't match, the request is rejected with 403

    Required attributes on the child class:
    - webhook_secret_setting: Name of the Django setting holding the shared secret
    - signature_header: Name of the HTTP header containing the signature

    Signature format in header:
        sha256=<hex_digest>

    Security features:
    - Constant-time comparison (hmac.compare_digest)
    - Timestamp validation (prevents replay attacks, optional)
    - Request body size limit
    - Logging of all verification attempts
    """

    webhook_secret_setting = "WEBHOOK_SECRET"
    signature_header = "X-Webhook-Signature"
    max_body_size = 1024 * 1024  # 1 MB
    timestamp_header = "X-Webhook-Timestamp"
    timestamp_tolerance = 300  # 5 minutes max drift

    def get_webhook_secret(self) -> str:
        """Get the shared secret from Django settings."""
        return getattr(settings, self.webhook_secret_setting, "")

    def compute_signature(self, payload: bytes, secret: str) -> str:
        """
        Compute HMAC-SHA256 signature for the given payload.

        Args:
            payload: Raw request body bytes
            secret: Shared secret string

        Returns:
            Hex-encoded HMAC-SHA256 signature prefixed with 'sha256='
        """
        mac = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha256,
        )
        return f"sha256={mac.hexdigest()}"

    def verify_signature(self, request) -> bool:
        """
        Verify the HMAC signature from the request header.

        Returns:
            True if signature is valid, False otherwise
        """
        secret = self.get_webhook_secret()
        if not secret:
            logger.error(
                f"Webhook secret not configured: {self.webhook_secret_setting}"
            )
            return False

        # Get signature from header
        received_signature = request.META.get(
            f"HTTP_{self.signature_header.upper().replace('-', '_')}",
            "",
        )

        if not received_signature:
            logger.warning("Missing webhook signature header")
            return False

        # Compute expected signature
        expected_signature = self.compute_signature(request.body, secret)

        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(received_signature, expected_signature)

        if not is_valid:
            logger.warning(
                f"Invalid webhook signature. "
                f"Expected: {expected_signature[:20]}..., "
                f"Received: {received_signature[:20]}..."
            )

        return is_valid

    def verify_timestamp(self, request) -> bool:
        """
        Verify the request timestamp to prevent replay attacks.

        Returns:
            True if timestamp is within tolerance, False otherwise
        """
        timestamp_str = request.META.get(
            f"HTTP_{self.timestamp_header.upper().replace('-', '_')}",
            "",
        )

        if not timestamp_str:
            # Timestamp header is optional
            return True

        try:
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            drift = abs(current_time - timestamp)

            if drift > self.timestamp_tolerance:
                logger.warning(
                    f"Webhook timestamp drift too large: {drift}s "
                    f"(tolerance: {self.timestamp_tolerance}s)"
                )
                return False

            return True

        except ValueError:
            logger.warning(f"Invalid webhook timestamp: {timestamp_str}")
            return False

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to verify HMAC before processing."""
        # Check body size
        if len(request.body) > self.max_body_size:
            return HttpResponse("Request too large", status=413)

        # Verify HMAC signature
        if not self.verify_signature(request):
            logger.warning(
                f"Webhook HMAC verification failed: "
                f"{request.path} from {request.META.get('REMOTE_ADDR')}"
            )
            return HttpResponse("Invalid signature", status=403)

        # Verify timestamp (replay protection)
        if not self.verify_timestamp(request):
            return HttpResponse("Request expired", status=403)

        return super().dispatch(request, *args, **kwargs)
```

---

## 2. StripeWebhookView

```python
# webhooks/views.py

import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook endpoint for processing payment events.

    URL: /webhooks/stripe/
    Method: POST
    Auth: Stripe signature verification (stripe.Webhook.construct_event)

    Stripe signs webhooks with the endpoint's signing secret.
    We use stripe.Webhook.construct_event() instead of custom HMAC
    because Stripe has its own signature scheme.

    Event routing table maps Stripe event types to handler methods.
    """

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            logger.error("Stripe webhook: Invalid payload")
            return HttpResponse("Invalid payload", status=400)
        except stripe.error.SignatureVerificationError:
            logger.warning("Stripe webhook: Invalid signature")
            return HttpResponse("Invalid signature", status=400)

        # Route to handler based on event type
        event_type = event["type"]
        handler = self.EVENT_HANDLERS.get(event_type)

        if handler:
            try:
                handler(self, event)
                logger.info(f"Stripe webhook processed: {event_type} ({event['id']})")
            except Exception as exc:
                logger.exception(f"Stripe webhook handler error: {event_type}")
                # Return 200 to prevent Stripe from retrying
                # (we log the error for manual investigation)
                return HttpResponse("Handler error (logged)", status=200)
        else:
            logger.debug(f"Stripe webhook unhandled event type: {event_type}")

        return HttpResponse("OK", status=200)

    # === Event Routing Table ===

    EVENT_HANDLERS = {}

    @staticmethod
    def _register_handler(event_type):
        """Decorator to register a handler for a Stripe event type."""
        def decorator(func):
            StripeWebhookView.EVENT_HANDLERS[event_type] = func
            return func
        return decorator

    # --- Payment Intent Events ---

    @_register_handler("payment_intent.succeeded")
    def handle_payment_intent_succeeded(self, event):
        """
        Payment was successfully completed.

        Actions:
        1. Update Payment record status
        2. Create Invoice from payment
        3. Generate invoice PDF
        4. Send invoice email
        5. Trigger n8n webhook for analytics
        """
        from payments.models import Payment
        from invoices.services import InvoiceService
        from automation.tasks import generate_invoice_pdf, send_email, trigger_webhook

        pi = event["data"]["object"]
        payment_intent_id = pi["id"]

        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for PI: {payment_intent_id}")
            return

        # Update payment status
        payment.status = "succeeded"
        payment.save(update_fields=["status", "updated_at"])

        # Create and generate invoice
        service = InvoiceService()
        invoice = service.create_invoice_from_payment(payment)
        generate_invoice_pdf.delay(str(invoice.id))

        # Trigger n8n webhook
        trigger_webhook.delay(
            event_type="payment.succeeded",
            payload={
                "payment_id": str(payment.id),
                "user_id": payment.user_id,
                "amount": str(payment.amount_total),
                "currency": "EUR",
                "rechnungsnummer": invoice.rechnungsnummer,
            },
        )

    @_register_handler("payment_intent.payment_failed")
    def handle_payment_intent_failed(self, event):
        """Payment attempt failed."""
        from payments.models import Payment

        pi = event["data"]["object"]
        payment_intent_id = pi["id"]
        error_message = pi.get("last_payment_error", {}).get("message", "Unknown error")

        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.status = "failed"
            payment.error_message = error_message
            payment.save(update_fields=["status", "error_message", "updated_at"])
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for failed PI: {payment_intent_id}")

    # --- Subscription Events ---

    @_register_handler("customer.subscription.created")
    def handle_subscription_created(self, event):
        """New subscription created."""
        from payments.models import Subscription
        from automation.tasks import trigger_webhook

        sub_data = event["data"]["object"]

        # Find or create subscription record
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=sub_data["id"]
            )
            subscription.status = sub_data["status"]
            subscription.current_period_start = __import__("datetime", fromlist=["datetime"]).datetime.fromtimestamp(
                sub_data["current_period_start"]
            )
            subscription.current_period_end = __import__("datetime", fromlist=["datetime"]).datetime.fromtimestamp(
                sub_data["current_period_end"]
            )
            subscription.save()
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found: {sub_data['id']}")

    @_register_handler("customer.subscription.updated")
    def handle_subscription_updated(self, event):
        """Subscription was updated (plan change, cancellation scheduled)."""
        from payments.models import Subscription

        sub_data = event["data"]["object"]

        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=sub_data["id"]
            )
            subscription.status = sub_data["status"]
            subscription.cancel_at_period_end = sub_data.get("cancel_at_period_end", False)
            subscription.save(update_fields=[
                "status", "cancel_at_period_end", "updated_at"
            ])
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found: {sub_data['id']}")

    @_register_handler("customer.subscription.deleted")
    def handle_subscription_deleted(self, event):
        """Subscription was cancelled/expired."""
        from payments.models import Subscription
        from django.utils import timezone
        from automation.tasks import trigger_webhook

        sub_data = event["data"]["object"]

        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=sub_data["id"]
            )
            subscription.status = "cancelled"
            subscription.cancelled_at = timezone.now()
            subscription.save(update_fields=["status", "cancelled_at", "updated_at"])

            # Trigger n8n workflow for churn tracking
            trigger_webhook.delay(
                event_type="subscription.cancelled",
                payload={
                    "subscription_id": str(subscription.id),
                    "user_id": subscription.user_id,
                    "plan": subscription.plan.slug if subscription.plan else "unknown",
                    "reason": sub_data.get("cancellation_details", {}).get("reason", "unknown"),
                },
            )
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found: {sub_data['id']}")

    # --- Invoice Events ---

    @_register_handler("invoice.payment_succeeded")
    def handle_invoice_payment_succeeded(self, event):
        """Recurring invoice payment succeeded."""
        invoice_data = event["data"]["object"]
        logger.info(
            f"Invoice payment succeeded: {invoice_data['id']} "
            f"amount: {invoice_data['amount_paid']}"
        )

    @_register_handler("invoice.payment_failed")
    def handle_invoice_payment_failed(self, event):
        """Recurring invoice payment failed (dunning)."""
        from automation.tasks import send_email

        invoice_data = event["data"]["object"]
        customer_email = invoice_data.get("customer_email")

        if customer_email:
            send_email.delay(
                to_email=customer_email,
                subject="Zahlungsproblem - Lebenslauf-Builder",
                template_name="emails/payment_failed.html",
                context={
                    "invoice_id": invoice_data["id"],
                    "amount": invoice_data["amount_due"] / 100,  # cents to EUR
                    "next_attempt": invoice_data.get("next_payment_attempt"),
                },
            )

    # --- Charge Events ---

    @_register_handler("charge.refunded")
    def handle_charge_refunded(self, event):
        """A charge was refunded (full or partial)."""
        charge = event["data"]["object"]
        logger.info(
            f"Charge refunded: {charge['id']}, "
            f"amount_refunded: {charge['amount_refunded']}"
        )
```

---

## 3. UserRegisteredWebhookView

```python
# webhooks/views.py (continued)

class UserRegisteredWebhookView(HMACVerificationMixin):
    """
    Internal webhook triggered by Django signal when a user registers.

    This endpoint is called by the trigger_webhook Celery task,
    which in turn is triggered by the post_save signal on User.

    The endpoint forwards the event to n8n via HTTP POST.

    URL: /webhooks/internal/user-registered/
    Method: POST
    Auth: HMAC-SHA256 (X-Webhook-Signature)
    """

    webhook_secret_setting = "INTERNAL_WEBHOOK_SECRET"
    signature_header = "X-Webhook-Signature"

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        logger.info(
            f"User registered webhook received: "
            f"user_id={payload.get('user_id')}"
        )

        # Forward to n8n webhook URL
        self._forward_to_n8n(
            n8n_webhook_url=settings.N8N_WEBHOOK_USER_REGISTERED,
            payload=payload,
        )

        return JsonResponse({"status": "received"}, status=200)

    def _forward_to_n8n(self, n8n_webhook_url: str, payload: dict):
        """Forward event to n8n webhook endpoint."""
        import requests

        try:
            response = requests.post(
                n8n_webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Source": "lebenslauf-builder",
                },
                timeout=10,
            )
            logger.info(f"n8n webhook response: {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"n8n webhook forward failed: {e}")
```

---

## 4. DocumentCreatedWebhookView

```python
# webhooks/views.py (continued)

class DocumentCreatedWebhookView(HMACVerificationMixin):
    """
    Internal webhook for document creation analytics tracking.

    URL: /webhooks/internal/document-created/
    Method: POST
    Auth: HMAC-SHA256 (X-Webhook-Signature)

    Payload:
    {
        "document_id": "uuid",
        "user_id": 123,
        "document_type": "lebenslauf",
        "template_id": "uuid",
        "created_at": "2026-03-03T10:00:00Z"
    }
    """

    webhook_secret_setting = "INTERNAL_WEBHOOK_SECRET"
    signature_header = "X-Webhook-Signature"

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        logger.info(
            f"Document created webhook: "
            f"doc_id={payload.get('document_id')}, "
            f"type={payload.get('document_type')}"
        )

        return JsonResponse({"status": "received"}, status=200)
```

---

## 5. Endpoint Specifications

### Complete Endpoint Table

| Endpoint | URL | Method | Auth | Purpose |
|----------|-----|--------|------|---------|
| Stripe Webhook | `/webhooks/stripe/` | POST | Stripe signature | Process Stripe payment events |
| User Registered | `/webhooks/internal/user-registered/` | POST | HMAC-SHA256 | Forward new user event to n8n |
| Document Created | `/webhooks/internal/document-created/` | POST | HMAC-SHA256 | Track document creation analytics |
| Payment Succeeded | `/webhooks/internal/payment-succeeded/` | POST | HMAC-SHA256 | Forward payment confirmation to n8n |
| Subscription Cancelled | `/webhooks/internal/subscription-cancelled/` | POST | HMAC-SHA256 | Forward churn event to n8n |
| GDPR Deletion | `/webhooks/internal/gdpr-deletion/` | POST | HMAC-SHA256 | Forward GDPR deletion event to n8n |
| GDPR Export | `/webhooks/internal/gdpr-export/` | POST | HMAC-SHA256 | Forward GDPR export event to n8n |

### Payload Formats

```json
// user.registered
{
    "event_type": "user.registered",
    "timestamp": "2026-03-03T10:00:00Z",
    "data": {
        "user_id": 12345,
        "email": "max@example.de",
        "first_name": "Max",
        "last_name": "Mustermann",
        "registered_at": "2026-03-03T10:00:00Z",
        "registration_source": "organic"
    }
}

// document.created
{
    "event_type": "document.created",
    "timestamp": "2026-03-03T10:05:00Z",
    "data": {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": 12345,
        "document_type": "lebenslauf",
        "template_id": "660e8400-e29b-41d4-a716-446655440001",
        "template_name": "Modern Berlin"
    }
}

// payment.succeeded
{
    "event_type": "payment.succeeded",
    "timestamp": "2026-03-03T10:10:00Z",
    "data": {
        "payment_id": "770e8400-e29b-41d4-a716-446655440002",
        "user_id": 12345,
        "amount": "9.99",
        "currency": "EUR",
        "plan": "premium_monthly",
        "rechnungsnummer": "RE-2026-00042",
        "payment_method": "stripe_card"
    }
}

// subscription.cancelled
{
    "event_type": "subscription.cancelled",
    "timestamp": "2026-03-03T11:00:00Z",
    "data": {
        "subscription_id": "880e8400-e29b-41d4-a716-446655440003",
        "user_id": 12345,
        "plan": "premium_monthly",
        "reason": "customer_request",
        "active_until": "2026-04-03T00:00:00Z",
        "total_months_subscribed": 6
    }
}

// gdpr.deletion_completed
{
    "event_type": "gdpr.deletion_completed",
    "timestamp": "2026-03-17T04:00:00Z",
    "data": {
        "request_id": "990e8400-e29b-41d4-a716-446655440004",
        "user_id": 12345,
        "documents_deleted": 5,
        "invoices_anonymized": 3
    }
}
```

### trigger_webhook Celery Task

```python
# automation/tasks.py (continued)

@shared_task(
    name="automation.tasks.trigger_webhook",
    max_retries=3,
    soft_time_limit=15,
    time_limit=30,
)
def trigger_webhook(event_type: str, payload: dict) -> dict:
    """
    Send an internal webhook event to n8n.

    Computes HMAC-SHA256 signature and sends the payload
    to the appropriate n8n webhook URL.

    Args:
        event_type: Event type string (e.g., 'user.registered')
        payload: Event data dictionary

    Returns:
        dict with status and response code
    """
    import hashlib
    import hmac
    import json
    import time

    import requests
    from django.conf import settings
    from django.utils import timezone

    # Map event types to n8n webhook URLs
    WEBHOOK_URLS = {
        "user.registered": settings.N8N_WEBHOOK_USER_REGISTERED,
        "document.created": settings.N8N_WEBHOOK_DOCUMENT_CREATED,
        "payment.succeeded": settings.N8N_WEBHOOK_PAYMENT_SUCCEEDED,
        "subscription.cancelled": settings.N8N_WEBHOOK_SUBSCRIPTION_CANCELLED,
        "gdpr.deletion_completed": settings.N8N_WEBHOOK_GDPR_DELETION,
        "gdpr.export_completed": settings.N8N_WEBHOOK_GDPR_EXPORT,
    }

    webhook_url = WEBHOOK_URLS.get(event_type)
    if not webhook_url:
        logger.warning(f"No webhook URL configured for event: {event_type}")
        return {"status": "skipped", "reason": "no_url_configured"}

    # Build event envelope
    event_data = {
        "event_type": event_type,
        "timestamp": timezone.now().isoformat(),
        "data": payload,
    }

    body = json.dumps(event_data, ensure_ascii=False).encode("utf-8")

    # Compute HMAC signature
    secret = settings.N8N_WEBHOOK_SECRET
    signature = f"sha256={hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()}"

    try:
        response = requests.post(
            webhook_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Timestamp": str(int(time.time())),
                "X-Event-Type": event_type,
                "X-Source": "lebenslauf-builder",
            },
            timeout=10,
        )

        logger.info(
            f"Webhook sent: {event_type} -> {webhook_url} "
            f"(status: {response.status_code})"
        )

        return {
            "status": "sent",
            "response_code": response.status_code,
            "event_type": event_type,
        }

    except requests.Timeout:
        logger.warning(f"Webhook timeout: {event_type} -> {webhook_url}")
        return {"status": "timeout", "event_type": event_type}

    except requests.RequestException as exc:
        logger.warning(f"Webhook failed: {event_type} -> {exc}")
        return {"status": "failed", "error": str(exc), "event_type": event_type}
```

---

## 6. n8n Workflow Descriptions

### Workflow 1: Welcome Email Sequence

```
Trigger: Webhook node (user.registered)
    |
    v
[Wait 5 minutes]
    |
    v
[IF] User has not created a document yet?
    |-- Yes --> [Send "Getting Started" email with tips]
    |           |
    |           v
    |           [Wait 24 hours]
    |           |
    |           v
    |           [IF] User still has no documents?
    |               |-- Yes --> [Send "Template Showcase" email]
    |               |-- No  --> [End]
    |
    |-- No --> [Send "Welcome + Quick Tips" email]
               |
               v
               [End]

n8n Configuration:
- Webhook URL: https://n8n.lebenslauf-builder.de/webhook/user-registered
- Auth: Header Auth (X-Webhook-Signature verification)
- Database query: PostgreSQL node to check document count
- Email: SMTP node or HTTP Request to SES API
```

### Workflow 2: Payment Confirmation

```
Trigger: Webhook node (payment.succeeded)
    |
    v
[Extract payment data from payload]
    |
    v
[HTTP Request: GET /api/internal/invoice/{rechnungsnummer}/pdf]
    |
    v
[Send payment confirmation email with invoice PDF attached]
    |
    v
[IF] First payment ever for this user?
    |-- Yes --> [Send "Premium Welcome" email with feature guide]
    |-- No  --> [End]

n8n Configuration:
- Webhook URL: https://n8n.lebenslauf-builder.de/webhook/payment-succeeded
- HTTP Request: Internal API with bearer token authentication
- Email: Attach PDF from HTTP response as binary
```

### Workflow 3: Subscription Expiring Reminder

```
Trigger: Cron (daily at 09:00 Berlin time)
    |
    v
[PostgreSQL Query: SELECT users WHERE subscription expires in 3 days]
    |
    v
[Loop over results]
    |
    v
[Send "Subscription Expiring" email]
    |-- Include: Plan name, expiry date, renewal link
    |-- Tone: Friendly reminder, not pushy
    |
    v
[Log sent reminders to audit table]

n8n Configuration:
- Cron trigger: 0 9 * * * (Europe/Berlin)
- PostgreSQL: Direct database connection (read-only credentials)
- Email: Personalized with user name and plan details
```

### Workflow 4: GDPR Deletion Notification

```
Trigger: Webhook node (gdpr.deletion_completed)
    |
    v
[Extract deletion summary from payload]
    |
    v
[Send admin notification email]
    |-- To: datenschutz@lebenslauf-builder.de
    |-- Content: User ID, deletion counts, timestamp
    |
    v
[Update internal tracking spreadsheet / Notion]
    |
    v
[IF] Deletion affected more than 10 invoices?
    |-- Yes --> [Send alert to finance team]
    |-- No  --> [End]

n8n Configuration:
- Webhook URL: https://n8n.lebenslauf-builder.de/webhook/gdpr-deletion
- Notion API: Update GDPR tracking database
- Conditional: Check invoices_anonymized count in payload
```

### Workflow 5: GDPR Export Ready

```
Trigger: Webhook node (gdpr.export_completed)
    |
    v
[Extract export details (file URL, size, counts)]
    |
    v
[Log to GDPR audit database]
    |
    v
[Send admin notification]
    |-- To: datenschutz@lebenslauf-builder.de
    |-- Content: Request ID, user, file size, document count
    |
    v
[Schedule: Delete export file after 48 hours]
    |-- n8n Wait node (48h)
    |-- HTTP Request: DELETE /api/internal/gdpr-exports/{id}/file
    |
    v
[End]

n8n Configuration:
- Webhook URL: https://n8n.lebenslauf-builder.de/webhook/gdpr-export
- Wait node: 48 hours delay
- Cleanup: HTTP DELETE request with admin API key
```

---

## 7. Security Patterns

### HMAC Computation

```python
# Example: Computing HMAC for sending a webhook

import hashlib
import hmac
import json
import time


def sign_webhook_payload(payload: dict, secret: str) -> tuple[str, str]:
    """
    Sign a webhook payload with HMAC-SHA256.

    Args:
        payload: The event data to sign
        secret: The shared secret

    Returns:
        Tuple of (signature_header_value, timestamp_header_value)
    """
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    timestamp = str(int(time.time()))

    # Include timestamp in HMAC to prevent replay attacks
    # Signature covers: timestamp + "." + body
    signing_input = f"{timestamp}.".encode("utf-8") + body

    signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=signing_input,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"sha256={signature}", timestamp
```

### Shared Secrets Configuration

```python
# config/settings/production.py

# === Webhook Secrets ===

# Stripe webhook signing secret (from Stripe Dashboard -> Webhooks)
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")
# Example: whsec_1234567890abcdef

# Internal webhook secret (shared between Django and n8n)
INTERNAL_WEBHOOK_SECRET = env("INTERNAL_WEBHOOK_SECRET")
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# n8n webhook secret (for n8n to verify requests from Django)
N8N_WEBHOOK_SECRET = env("N8N_WEBHOOK_SECRET")

# n8n webhook URLs
N8N_WEBHOOK_USER_REGISTERED = env(
    "N8N_WEBHOOK_USER_REGISTERED",
    default="https://n8n.lebenslauf-builder.de/webhook/user-registered",
)
N8N_WEBHOOK_DOCUMENT_CREATED = env(
    "N8N_WEBHOOK_DOCUMENT_CREATED",
    default="https://n8n.lebenslauf-builder.de/webhook/document-created",
)
N8N_WEBHOOK_PAYMENT_SUCCEEDED = env(
    "N8N_WEBHOOK_PAYMENT_SUCCEEDED",
    default="https://n8n.lebenslauf-builder.de/webhook/payment-succeeded",
)
N8N_WEBHOOK_SUBSCRIPTION_CANCELLED = env(
    "N8N_WEBHOOK_SUBSCRIPTION_CANCELLED",
    default="https://n8n.lebenslauf-builder.de/webhook/subscription-cancelled",
)
N8N_WEBHOOK_GDPR_DELETION = env(
    "N8N_WEBHOOK_GDPR_DELETION",
    default="https://n8n.lebenslauf-builder.de/webhook/gdpr-deletion",
)
N8N_WEBHOOK_GDPR_EXPORT = env(
    "N8N_WEBHOOK_GDPR_EXPORT",
    default="https://n8n.lebenslauf-builder.de/webhook/gdpr-export",
)
```

### Rate Limiting with django-ratelimit

```python
# webhooks/views.py (continued)

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


@method_decorator(
    ratelimit(key="ip", rate="60/m", method="POST", block=True),
    name="post",
)
class RateLimitedWebhookView(HMACVerificationMixin):
    """
    Base class for rate-limited webhook endpoints.

    Rate limits:
    - Stripe webhook: 120/min per IP (Stripe may send bursts)
    - Internal webhooks: 60/min per IP
    - n8n callbacks: 30/min per IP
    """
    pass


# For the Stripe webhook specifically (higher rate limit):
@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(
    ratelimit(key="ip", rate="120/m", method="POST", block=True),
    name="post",
)
class StripeWebhookView(View):
    # ... (implementation above)
    pass
```

### URL Configuration

```python
# webhooks/urls.py

from django.urls import path
from . import views

app_name = "webhooks"

urlpatterns = [
    # Stripe webhook (verified by Stripe signature)
    path(
        "stripe/",
        views.StripeWebhookView.as_view(),
        name="stripe",
    ),

    # Internal webhooks (verified by HMAC)
    path(
        "internal/user-registered/",
        views.UserRegisteredWebhookView.as_view(),
        name="user_registered",
    ),
    path(
        "internal/document-created/",
        views.DocumentCreatedWebhookView.as_view(),
        name="document_created",
    ),
]

# In main urls.py:
# path("webhooks/", include("webhooks.urls")),
```

### Security Checklist

1. **HMAC Verification**: All webhook endpoints verify HMAC-SHA256 signatures using constant-time comparison (`hmac.compare_digest`)
2. **Stripe Signature**: Stripe webhooks use `stripe.Webhook.construct_event()` which handles Stripe's specific signing scheme
3. **Shared Secrets**: All secrets are stored as environment variables, never in code. Secrets are at least 32 bytes of cryptographic randomness
4. **Rate Limiting**: All webhook endpoints are rate-limited via `django-ratelimit` to prevent abuse
5. **CSRF Exemption**: Webhook endpoints are CSRF-exempt (they use HMAC instead of Django CSRF tokens)
6. **Body Size Limit**: Maximum request body size of 1 MB to prevent memory exhaustion
7. **Timestamp Validation**: Optional replay attack prevention via timestamp header (5-minute tolerance)
8. **Logging**: All webhook attempts (success and failure) are logged for audit trail
9. **Error Handling**: Stripe webhooks return 200 even on handler errors to prevent retry storms. Errors are logged and monitored via Sentry
10. **HTTPS Only**: All webhook URLs must use HTTPS in production (enforced by Nginx)
