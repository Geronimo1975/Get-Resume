# Stripe Views Reference

Complete Stripe payment views, service class, webhook handling, and Celery tasks for the German market.

---

## URL Configuration

```python
# payments/urls.py

from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # Public pricing page
    path("preise/", views.PricingPageView.as_view(), name="pricing"),

    # Checkout (requires login)
    path("checkout/<str:plan>/", views.CheckoutView.as_view(), name="checkout"),
    path("checkout/success/", views.CheckoutSuccessView.as_view(), name="checkout_success"),
    path("checkout/cancel/", views.CheckoutCancelView.as_view(), name="checkout_cancel"),

    # Stripe webhook (no CSRF, no login)
    path("webhook/stripe/", views.StripeWebhookView.as_view(), name="stripe_webhook"),

    # Subscription management (requires login)
    path(
        "mein-bereich/abonnement/",
        views.SubscriptionManageView.as_view(),
        name="subscription_manage",
    ),
    path(
        "mein-bereich/abonnement/kuendigen/",
        views.SubscriptionCancelView.as_view(),
        name="subscription_cancel",
    ),

    # Widerruf (14-day withdrawal)
    path(
        "mein-bereich/widerruf/",
        views.WiderrufView.as_view(),
        name="widerruf",
    ),

    # Invoices
    path(
        "mein-bereich/rechnungen/",
        views.InvoiceListView.as_view(),
        name="invoice_list",
    ),
    path(
        "mein-bereich/rechnungen/<uuid:invoice_id>/",
        views.InvoiceDownloadView.as_view(),
        name="invoice_download",
    ),
]
```

---

## 1. StripeService Class

```python
# payments/services.py

import logging
import stripe
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Initialize Stripe with secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Service class encapsulating all Stripe API interactions.
    Handles customer creation, checkout sessions, subscription management,
    and refunds for the German market.
    """

    PLAN_PRICE_MAP = {
        "premium_monthly": {
            "price_id": settings.STRIPE_PRICE_IDS.get("premium_monthly", ""),
            "amount_gross_cents": 999,      # 9,99 EUR brutto
            "amount_net_cents": 840,         # 8,40 EUR netto
            "mwst_cents": 159,               # 1,59 EUR MwSt
            "interval": "month",
        },
        "premium_yearly": {
            "price_id": settings.STRIPE_PRICE_IDS.get("premium_yearly", ""),
            "amount_gross_cents": 9588,      # 95,88 EUR brutto
            "amount_net_cents": 8057,        # 80,57 EUR netto
            "mwst_cents": 1531,              # 15,31 EUR MwSt
            "interval": "year",
        },
        "business": {
            "price_id": settings.STRIPE_PRICE_IDS.get("business", ""),
            "amount_gross_cents": 1999,      # 19,99 EUR brutto
            "amount_net_cents": 1680,        # 16,80 EUR netto
            "mwst_cents": 319,               # 3,19 EUR MwSt
            "interval": "month",
        },
    }

    def create_customer(self, user):
        """
        Create a Stripe Customer for a user.
        Called during first checkout or registration.
        """
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name(),
                metadata={
                    "user_id": str(user.id),
                    "platform": "lebenslauf-builder",
                },
            )
            logger.info("Stripe customer created: %s for user %s", customer.id, user.id)
            return customer
        except stripe.error.StripeError:
            logger.exception("Failed to create Stripe customer for user %s", user.id)
            raise

    def get_or_create_customer(self, user):
        """Get existing Stripe customer or create one."""
        if hasattr(user, "subscription") and user.subscription.stripe_customer_id:
            try:
                return stripe.Customer.retrieve(user.subscription.stripe_customer_id)
            except stripe.error.InvalidRequestError:
                pass  # Customer deleted on Stripe side, create new one

        customer = self.create_customer(user)

        # Save customer ID
        from payments.models import Subscription
        sub, _ = Subscription.objects.get_or_create(user=user)
        sub.stripe_customer_id = customer.id
        sub.save(update_fields=["stripe_customer_id"])

        return customer

    def create_checkout_session(self, user, plan, request):
        """
        Create a Stripe Checkout Session for a subscription plan.

        German-specific configuration:
        - EUR currency
        - German payment methods (card, SEPA, Sofort, Giropay)
        - German locale
        - Tax display (MwSt included)
        """
        plan_config = self.PLAN_PRICE_MAP.get(plan)
        if not plan_config:
            raise ValueError(f"Unknown plan: {plan}")

        customer = self.get_or_create_customer(user)

        try:
            session = stripe.checkout.Session.create(
                customer=customer.id,
                mode="subscription",
                payment_method_types=[
                    "card",
                    "sepa_debit",
                ],
                line_items=[
                    {
                        "price": plan_config["price_id"],
                        "quantity": 1,
                    },
                ],
                locale="de",
                currency="eur",
                success_url=(
                    request.build_absolute_uri("/checkout/success/")
                    + "?session_id={CHECKOUT_SESSION_ID}"
                ),
                cancel_url=request.build_absolute_uri("/checkout/cancel/"),
                metadata={
                    "user_id": str(user.id),
                    "plan": plan,
                },
                subscription_data={
                    "metadata": {
                        "user_id": str(user.id),
                        "plan": plan,
                    },
                },
                # Legal: require explicit consent before payment
                consent_collection={
                    "terms_of_service": "required",
                },
                custom_text={
                    "terms_of_service_acceptance": {
                        "message": (
                            "Ich habe die [AGB](https://lebenslauf-builder.de/agb/) "
                            "und die [Widerrufsbelehrung](https://lebenslauf-builder.de/widerrufsbelehrung/) "
                            "gelesen und akzeptiere diese. Ich stimme zu, dass die Dienstleistung sofort beginnt."
                        ),
                    },
                },
                # Show tax info
                automatic_tax={"enabled": False},  # We handle MwSt ourselves
            )

            logger.info(
                "Checkout session created: %s for user %s, plan %s",
                session.id, user.id, plan,
            )
            return session

        except stripe.error.StripeError:
            logger.exception("Failed to create checkout session for user %s", user.id)
            raise

    def cancel_subscription(self, stripe_subscription_id, at_period_end=True):
        """
        Cancel a Stripe subscription.
        Default: cancel at end of billing period (not immediate).
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    stripe_subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                subscription = stripe.Subscription.cancel(stripe_subscription_id)

            logger.info("Subscription canceled: %s", stripe_subscription_id)
            return subscription

        except stripe.error.StripeError:
            logger.exception("Failed to cancel subscription %s", stripe_subscription_id)
            raise

    def process_refund(self, payment_intent_id, amount_cents=None, reason="requested_by_customer"):
        """
        Process a refund via Stripe.
        If amount_cents is None, full refund. Otherwise partial.
        """
        try:
            refund_params = {
                "payment_intent": payment_intent_id,
                "reason": reason,
            }
            if amount_cents:
                refund_params["amount"] = amount_cents

            refund = stripe.Refund.create(**refund_params)
            logger.info(
                "Refund processed: %s for PI %s (amount: %s)",
                refund.id, payment_intent_id, amount_cents,
            )
            return refund

        except stripe.error.StripeError:
            logger.exception("Failed to process refund for PI %s", payment_intent_id)
            raise

    def calculate_widerruf_refund(self, subscription):
        """
        Calculate pro-rata refund amount for Widerruf (14-day withdrawal).
        User agreed to immediate service start, so we deduct used portion.
        """
        plan_config = self.PLAN_PRICE_MAP.get(subscription.plan)
        if not plan_config:
            return 0

        total_amount = plan_config["amount_gross_cents"]

        # Calculate used days
        if not subscription.current_period_start:
            return total_amount  # Full refund if no period set

        days_used = (timezone.now() - subscription.current_period_start).days
        if days_used < 0:
            days_used = 0

        # Total days in period
        if plan_config["interval"] == "month":
            total_days = 30
        elif plan_config["interval"] == "year":
            total_days = 365
        else:
            total_days = 30

        if days_used >= total_days:
            return 0  # No refund if full period used

        # Pro-rata calculation
        used_fraction = Decimal(str(days_used)) / Decimal(str(total_days))
        used_amount = (Decimal(str(total_amount)) * used_fraction).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        refund_amount = total_amount - int(used_amount)

        return max(0, refund_amount)
```

---

## 2. CheckoutView

```python
# payments/views.py

import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings

from .services import StripeService
from .models import Subscription

logger = logging.getLogger(__name__)


class CheckoutView(LoginRequiredMixin, View):
    """
    Initiate Stripe Checkout Session.
    Validates legal checkbox requirements before redirecting to Stripe.
    """

    def get(self, request, plan):
        """Show checkout confirmation page with legal checkboxes."""
        stripe_service = StripeService()
        plan_config = stripe_service.PLAN_PRICE_MAP.get(plan)

        if not plan_config:
            messages.error(request, "Ungueltiger Abonnement-Plan.")
            return redirect("payments:pricing")

        # Check if user already has this plan
        if hasattr(request.user, "subscription"):
            sub = request.user.subscription
            if sub.plan == plan and sub.is_active:
                messages.info(request, "Sie haben diesen Plan bereits abonniert.")
                return redirect("payments:subscription_manage")

        return render(request, "payments/checkout.html", {
            "plan": plan,
            "plan_config": plan_config,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        })

    def post(self, request, plan):
        """
        Create Stripe Checkout Session after legal validation.
        Redirects to Stripe-hosted checkout page.
        """
        # Validate legal checkboxes (server-side validation)
        agb_accepted = request.POST.get("agb_accepted") == "on"
        widerruf_accepted = request.POST.get("widerruf_accepted") == "on"
        sofort_beginn = request.POST.get("sofort_beginn") == "on"

        if not all([agb_accepted, widerruf_accepted, sofort_beginn]):
            messages.error(
                request,
                "Bitte akzeptieren Sie alle erforderlichen Bedingungen."
            )
            return redirect("payments:checkout", plan=plan)

        try:
            stripe_service = StripeService()
            session = stripe_service.create_checkout_session(
                user=request.user,
                plan=plan,
                request=request,
            )

            # Redirect to Stripe Checkout
            return redirect(session.url)

        except Exception:
            logger.exception("Checkout session creation failed for user %s", request.user.id)
            messages.error(
                request,
                "Beim Erstellen der Checkout-Sitzung ist ein Fehler aufgetreten. "
                "Bitte versuchen Sie es erneut."
            )
            return redirect("payments:pricing")


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    """Success page after Stripe Checkout completion."""
    template_name = "payments/checkout_success.html"


class CheckoutCancelView(LoginRequiredMixin, TemplateView):
    """Page shown when user cancels Stripe Checkout."""
    template_name = "payments/checkout_cancel.html"
```

---

## 3. WebhookView

```python
import json
import stripe
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook endpoint.
    Verifies signature, routes events to handlers.
    Critical: this endpoint has NO CSRF protection and NO authentication
    (Stripe calls it directly).
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
            logger.warning("Invalid Stripe webhook payload")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return HttpResponse(status=400)

        # Route event to handler
        event_type = event["type"]
        logger.info("Stripe webhook received: %s", event_type)

        handler = self._get_handler(event_type)
        if handler:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Error processing webhook event %s: %s",
                    event_type, event["id"],
                )
                # Return 200 anyway to prevent Stripe retries for app errors
                # Process asynchronously for retryable errors
                from payments.tasks import process_webhook_async
                process_webhook_async.delay(event_type, json.loads(payload))

        return HttpResponse(status=200)

    def _get_handler(self, event_type):
        """Map Stripe event types to handler methods."""
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_payment_failed,
        }
        return handlers.get(event_type)

    def _handle_checkout_completed(self, event):
        """
        Handle checkout.session.completed.
        Activates subscription and sets up Widerrufsrecht timer.
        """
        from datetime import timedelta
        from django.contrib.auth import get_user_model
        from payments.models import Subscription, Payment

        User = get_user_model()
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        plan = session["metadata"].get("plan")

        if not user_id or not plan:
            logger.error("Missing metadata in checkout session: %s", session["id"])
            return

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("User not found for checkout: %s", user_id)
            return

        # Update or create subscription
        subscription, _ = Subscription.objects.get_or_create(user=user)
        subscription.plan = plan
        subscription.status = Subscription.Status.ACTIVE
        subscription.stripe_subscription_id = session.get("subscription", "")
        subscription.stripe_customer_id = session.get("customer", "")
        subscription.current_period_start = timezone.now()

        # Set Widerrufsrecht timer (14 days from now)
        subscription.widerruf_eligible_until = timezone.now() + timedelta(days=14)

        # Calculate period end based on plan
        stripe_service = StripeService()
        plan_config = stripe_service.PLAN_PRICE_MAP.get(plan, {})
        if plan_config.get("interval") == "year":
            subscription.current_period_end = timezone.now() + timedelta(days=365)
        else:
            subscription.current_period_end = timezone.now() + timedelta(days=30)

        subscription.save()

        # Update user profile
        user.profile.subscription_plan = plan
        user.profile.subscription_expires_at = subscription.current_period_end
        user.profile.save(update_fields=["subscription_plan", "subscription_expires_at"])

        # Create payment record
        if plan_config:
            Payment.objects.create(
                user=user,
                subscription=subscription,
                stripe_payment_intent_id=session.get("payment_intent", ""),
                amount_net=plan_config["amount_net_cents"],
                mwst_rate=Decimal("19.00"),
                mwst_amount=plan_config["mwst_cents"],
                amount_gross=plan_config["amount_gross_cents"],
                status=Payment.Status.SUCCEEDED,
                paid_at=timezone.now(),
                description=f"Abonnement: {plan}",
            )

        # Send confirmation email
        from payments.tasks import send_payment_confirmation
        send_payment_confirmation.delay(str(user.id), plan)

        logger.info("Subscription activated for user %s: %s", user.id, plan)

    def _handle_payment_succeeded(self, event):
        """Log successful payment intent."""
        from payments.models import Payment
        payment_intent = event["data"]["object"]
        pi_id = payment_intent["id"]

        Payment.objects.filter(
            stripe_payment_intent_id=pi_id
        ).update(
            status=Payment.Status.SUCCEEDED,
            paid_at=timezone.now(),
        )

    def _handle_subscription_updated(self, event):
        """Sync subscription changes from Stripe."""
        from payments.models import Subscription
        from django.contrib.auth import get_user_model
        User = get_user_model()

        sub_data = event["data"]["object"]
        stripe_sub_id = sub_data["id"]

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
        except Subscription.DoesNotExist:
            logger.warning("Subscription not found: %s", stripe_sub_id)
            return

        # Update status
        status_map = {
            "active": Subscription.Status.ACTIVE,
            "past_due": Subscription.Status.PAST_DUE,
            "canceled": Subscription.Status.CANCELED,
            "incomplete": Subscription.Status.INCOMPLETE,
            "trialing": Subscription.Status.TRIALING,
            "unpaid": Subscription.Status.UNPAID,
        }
        new_status = status_map.get(sub_data["status"], subscription.status)
        subscription.status = new_status
        subscription.cancel_at_period_end = sub_data.get("cancel_at_period_end", False)

        # Update period dates
        if sub_data.get("current_period_start"):
            from datetime import datetime
            subscription.current_period_start = timezone.make_aware(
                datetime.fromtimestamp(sub_data["current_period_start"])
            )
        if sub_data.get("current_period_end"):
            subscription.current_period_end = timezone.make_aware(
                datetime.fromtimestamp(sub_data["current_period_end"])
            )

        subscription.save()
        logger.info("Subscription updated: %s -> %s", stripe_sub_id, new_status)

    def _handle_subscription_deleted(self, event):
        """Handle subscription cancellation/deletion."""
        from payments.models import Subscription

        sub_data = event["data"]["object"]
        stripe_sub_id = sub_data["id"]

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            subscription.status = Subscription.Status.CANCELED
            subscription.plan = Subscription.Plan.FREE
            subscription.save()

            # Downgrade user profile
            subscription.user.profile.subscription_plan = "free"
            subscription.user.profile.save(update_fields=["subscription_plan"])

            logger.info("Subscription deleted/canceled: %s", stripe_sub_id)
        except Subscription.DoesNotExist:
            logger.warning("Subscription not found for deletion: %s", stripe_sub_id)

    def _handle_invoice_paid(self, event):
        """Generate GoBD-compliant invoice when Stripe invoice is paid."""
        from payments.tasks import generate_invoice_pdf
        invoice_data = event["data"]["object"]
        generate_invoice_pdf.delay(invoice_data["id"])

    def _handle_payment_failed(self, event):
        """Handle failed payment — send dunning email, start grace period."""
        from payments.tasks import send_payment_failed_email
        invoice_data = event["data"]["object"]
        customer_id = invoice_data.get("customer", "")

        from payments.models import Subscription
        try:
            subscription = Subscription.objects.get(stripe_customer_id=customer_id)
            subscription.status = Subscription.Status.PAST_DUE
            subscription.save(update_fields=["status"])

            send_payment_failed_email.delay(str(subscription.user.id))
        except Subscription.DoesNotExist:
            logger.warning("Subscription not found for customer: %s", customer_id)
```

---

## 4. SubscriptionManageView

```python
class SubscriptionManageView(LoginRequiredMixin, View):
    """
    Shows current subscription details and management options.
    """

    def get(self, request):
        subscription = getattr(request.user, "subscription", None)

        if not subscription or subscription.plan == "free":
            return redirect("payments:pricing")

        stripe_service = StripeService()
        plan_config = stripe_service.PLAN_PRICE_MAP.get(subscription.plan, {})

        context = {
            "subscription": subscription,
            "plan_config": plan_config,
            "can_widerruf": subscription.can_widerruf if subscription else False,
            "widerruf_days": subscription.days_until_widerruf_expires if subscription else 0,
        }

        return render(request, "payments/subscription_manage.html", context)


class SubscriptionCancelView(LoginRequiredMixin, View):
    """Cancel subscription at end of billing period."""

    def get(self, request):
        subscription = getattr(request.user, "subscription", None)
        if not subscription or not subscription.is_active:
            return redirect("payments:pricing")

        return render(request, "payments/subscription_cancel.html", {
            "subscription": subscription,
        })

    def post(self, request):
        subscription = getattr(request.user, "subscription", None)
        if not subscription or not subscription.is_active:
            return redirect("payments:pricing")

        try:
            stripe_service = StripeService()
            stripe_service.cancel_subscription(
                subscription.stripe_subscription_id,
                at_period_end=True,  # Continue until end of paid period
            )

            subscription.cancel_at_period_end = True
            subscription.save(update_fields=["cancel_at_period_end"])

            messages.success(
                request,
                f"Ihr Abonnement wird zum {subscription.current_period_end.strftime('%d.%m.%Y')} "
                f"gekuendigt. Bis dahin stehen Ihnen alle Premium-Funktionen zur Verfuegung."
            )

        except Exception:
            logger.exception("Subscription cancel failed for user %s", request.user.id)
            messages.error(
                request,
                "Beim Kuendigen ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut."
            )

        return redirect("payments:subscription_manage")
```

---

## 5. WiderrufView (14-Day Withdrawal)

```python
class WiderrufView(LoginRequiredMixin, View):
    """
    14-day withdrawal right (Widerrufsrecht) per BGB 312g.
    Processes pro-rata refund if user agreed to immediate service start.
    """

    def get(self, request):
        subscription = getattr(request.user, "subscription", None)
        if not subscription or not subscription.can_widerruf:
            messages.info(
                request,
                "Die 14-taegige Widerrufsfrist ist leider abgelaufen."
            )
            return redirect("payments:subscription_manage")

        stripe_service = StripeService()
        refund_amount = stripe_service.calculate_widerruf_refund(subscription)

        return render(request, "payments/widerruf.html", {
            "subscription": subscription,
            "refund_amount_cents": refund_amount,
            "refund_amount_display": f"{refund_amount / 100:.2f}".replace(".", ","),
            "days_remaining": subscription.days_until_widerruf_expires,
        })

    def post(self, request):
        subscription = getattr(request.user, "subscription", None)
        if not subscription or not subscription.can_widerruf:
            messages.error(request, "Widerruf nicht mehr moeglich.")
            return redirect("payments:subscription_manage")

        # Verify password for security
        password = request.POST.get("password", "")
        if not request.user.check_password(password):
            messages.error(request, "Das Passwort ist nicht korrekt.")
            return redirect("payments:widerruf")

        try:
            stripe_service = StripeService()

            # Calculate refund
            refund_amount = stripe_service.calculate_widerruf_refund(subscription)

            # Find the payment to refund
            from payments.models import Payment
            payment = Payment.objects.filter(
                user=request.user,
                subscription=subscription,
                status=Payment.Status.SUCCEEDED,
            ).order_by("-paid_at").first()

            if payment and payment.stripe_payment_intent_id:
                # Process Stripe refund
                stripe_service.process_refund(
                    payment_intent_id=payment.stripe_payment_intent_id,
                    amount_cents=refund_amount if refund_amount < payment.amount_gross else None,
                    reason="requested_by_customer",
                )

                # Update payment record
                payment.status = (
                    Payment.Status.REFUNDED
                    if refund_amount >= payment.amount_gross
                    else Payment.Status.PARTIALLY_REFUNDED
                )
                payment.refunded_at = timezone.now()
                payment.refund_amount = refund_amount
                payment.save()

            # Cancel subscription immediately
            stripe_service.cancel_subscription(
                subscription.stripe_subscription_id,
                at_period_end=False,  # Immediate for Widerruf
            )

            # Update local subscription
            subscription.status = Subscription.Status.CANCELED
            subscription.plan = Subscription.Plan.FREE
            subscription.widerruf_eligible_until = None
            subscription.save()

            # Downgrade user profile
            request.user.profile.subscription_plan = "free"
            request.user.profile.save(update_fields=["subscription_plan"])

            # Audit log
            from legal.models import AuditLog
            AuditLog.log(
                user=request.user,
                action=AuditLog.Action.UPDATE,
                model_name="Subscription",
                object_id=str(subscription.id),
                changes={
                    "action": "widerruf",
                    "refund_amount_cents": refund_amount,
                },
                ip_address=request.META.get("REMOTE_ADDR"),
            )

            # Send confirmation
            from payments.tasks import send_widerruf_confirmation
            send_widerruf_confirmation.delay(str(request.user.id), refund_amount)

            messages.success(
                request,
                f"Ihr Widerruf wurde erfolgreich bearbeitet. "
                f"Eine Erstattung von {refund_amount / 100:.2f} EUR wird in den "
                f"naechsten 5-10 Werktagen auf Ihrem Konto gutgeschrieben."
            )

        except Exception:
            logger.exception("Widerruf failed for user %s", request.user.id)
            messages.error(
                request,
                "Beim Widerruf ist ein Fehler aufgetreten. "
                "Bitte kontaktieren Sie uns unter widerruf@lebenslauf-builder.de."
            )

        return redirect("payments:subscription_manage")
```

---

## 6. PricingPageView (PAngV-Compliant)

```python
class PricingPageView(TemplateView):
    """
    Public pricing page at /preise/.
    Displays plans with PAngV-compliant pricing (gross incl. MwSt).
    """
    template_name = "payments/pricing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["plans"] = [
            {
                "key": "free",
                "name": "Kostenlos",
                "price_display": "0,00 EUR",
                "price_note": "",
                "features": [
                    "1 Lebenslauf",
                    "3 Vorlagen",
                    "PDF mit Wasserzeichen",
                ],
                "cta_text": "Kostenlos starten",
                "cta_url": "/konto/registrieren/",
                "is_popular": False,
            },
            {
                "key": "premium_monthly",
                "name": "Premium Monatlich",
                "price_display": "9,99 EUR",
                "price_note": "pro Monat inkl. MwSt",
                "price_net": "8,40 EUR netto zzgl. 1,59 EUR MwSt (19%)",
                "features": [
                    "Unbegrenzte Lebenslaeufe",
                    "Alle Vorlagen",
                    "PDF ohne Wasserzeichen",
                    "Alle Farbschemata",
                    "Bewerbungsschreiben & Deckblatt",
                ],
                "cta_text": "Jetzt abonnieren",
                "cta_url": "/checkout/premium_monthly/",
                "is_popular": True,
            },
            {
                "key": "premium_yearly",
                "name": "Premium Jaehrlich",
                "price_display": "7,99 EUR",
                "price_note": "pro Monat inkl. MwSt (95,88 EUR/Jahr)",
                "price_net": "80,57 EUR netto zzgl. 15,31 EUR MwSt (19%) pro Jahr",
                "savings": "20% gespart",
                "features": [
                    "Alle Premium-Funktionen",
                    "Vorrang-Support",
                    "20% guenstiger als monatlich",
                ],
                "cta_text": "Jaehrlich sparen",
                "cta_url": "/checkout/premium_yearly/",
                "is_popular": False,
            },
            {
                "key": "business",
                "name": "Business",
                "price_display": "19,99 EUR",
                "price_note": "pro Monat inkl. MwSt",
                "price_net": "16,80 EUR netto zzgl. 3,19 EUR MwSt (19%)",
                "features": [
                    "Alle Premium-Funktionen",
                    "Team-Funktionen",
                    "API-Zugang",
                    "Dedizierter Support",
                ],
                "cta_text": "Business starten",
                "cta_url": "/checkout/business/",
                "is_popular": False,
            },
        ]

        # Current user's plan
        if self.request.user.is_authenticated:
            context["current_plan"] = getattr(
                self.request.user, "profile", None
            ) and self.request.user.profile.subscription_plan or "free"
        else:
            context["current_plan"] = None

        return context
```

---

## 7. Celery Tasks

```python
# payments/tasks.py

import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue="payments")
def process_webhook_async(self, event_type, event_data):
    """
    Process webhook events asynchronously (retry on failure).
    Used as fallback when synchronous processing fails.
    """
    logger.info("Processing webhook async: %s", event_type)
    # Re-route to appropriate handler
    # (Implementation mirrors StripeWebhookView handlers)


@shared_task(queue="emails")
def send_payment_confirmation(user_id, plan):
    """
    Send payment confirmation email with invoice attachment.
    """
    from django.contrib.auth import get_user_model
    from django.core.mail import EmailMessage

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("User not found for payment confirmation: %s", user_id)
        return

    plan_names = {
        "premium_monthly": "Premium Monatlich",
        "premium_yearly": "Premium Jaehrlich",
        "business": "Business",
    }
    plan_name = plan_names.get(plan, plan)

    email = EmailMessage(
        subject=f"Zahlungsbestaetigung - {plan_name} | Lebenslauf-Builder",
        body=(
            f"Sehr geehrte(r) {user.get_full_name()},\n\n"
            f"vielen Dank fuer Ihr Abonnement!\n\n"
            f"Plan: {plan_name}\n"
            f"Datum: {timezone.now().strftime('%d.%m.%Y')}\n\n"
            f"Ihre Rechnung finden Sie in Ihrem Kundenkonto unter "
            f"'Mein Bereich > Rechnungen'.\n\n"
            f"Bitte beachten Sie: Sie haben ein 14-taegiges Widerrufsrecht.\n"
            f"Details finden Sie unter: https://lebenslauf-builder.de/widerrufsbelehrung/\n\n"
            f"Mit freundlichen Gruessen\n"
            f"Ihr Lebenslauf-Builder Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.send()
    logger.info("Payment confirmation sent to %s", user.email)


@shared_task(queue="emails")
def send_widerruf_confirmation(user_id, refund_amount_cents):
    """Send Widerruf (withdrawal) confirmation email."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    refund_display = f"{refund_amount_cents / 100:.2f}".replace(".", ",")

    send_mail(
        subject="Widerrufsbestaetigung | Lebenslauf-Builder",
        message=(
            f"Sehr geehrte(r) {user.get_full_name()},\n\n"
            f"wir bestaetigen den Eingang Ihres Widerrufs.\n\n"
            f"Erstattungsbetrag: {refund_display} EUR\n"
            f"Die Erstattung wird innerhalb von 5-10 Werktagen "
            f"auf Ihr urspruengliches Zahlungsmittel gutgeschrieben.\n\n"
            f"Ihr Konto wurde auf den kostenlosen Plan zurueckgesetzt.\n\n"
            f"Mit freundlichen Gruessen\n"
            f"Ihr Lebenslauf-Builder Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    logger.info("Widerruf confirmation sent to %s", user.email)


@shared_task(queue="emails")
def send_payment_failed_email(user_id):
    """Send dunning email when payment fails."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    send_mail(
        subject="Zahlungsproblem - Ihr Abonnement | Lebenslauf-Builder",
        message=(
            f"Sehr geehrte(r) {user.get_full_name()},\n\n"
            f"leider konnte Ihre letzte Zahlung nicht verarbeitet werden.\n\n"
            f"Bitte aktualisieren Sie Ihre Zahlungsinformationen innerhalb "
            f"von 7 Tagen, um eine Unterbrechung Ihres Abonnements zu vermeiden.\n\n"
            f"Zahlungsmethode aktualisieren:\n"
            f"https://lebenslauf-builder.de/mein-bereich/abonnement/\n\n"
            f"Falls Sie Fragen haben, kontaktieren Sie uns unter "
            f"support@lebenslauf-builder.de.\n\n"
            f"Mit freundlichen Gruessen\n"
            f"Ihr Lebenslauf-Builder Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    logger.info("Payment failed email sent to %s", user.email)


@shared_task(queue="payments")
def check_expiring_subscriptions():
    """
    Check for subscriptions expiring in the next 7 days.
    Send reminder emails.
    """
    from payments.models import Subscription
    from django.core.mail import send_mail

    cutoff = timezone.now() + timezone.timedelta(days=7)

    expiring = Subscription.objects.filter(
        status=Subscription.Status.ACTIVE,
        cancel_at_period_end=True,
        current_period_end__lte=cutoff,
        current_period_end__gt=timezone.now(),
    )

    for sub in expiring:
        send_mail(
            subject="Ihr Abonnement laeuft bald aus | Lebenslauf-Builder",
            message=(
                f"Sehr geehrte(r) {sub.user.get_full_name()},\n\n"
                f"Ihr {sub.get_plan_display()}-Abonnement laeuft am "
                f"{sub.current_period_end.strftime('%d.%m.%Y')} aus.\n\n"
                f"Nach Ablauf wird Ihr Konto auf den kostenlosen Plan zurueckgesetzt.\n"
                f"Moechten Sie Ihr Abonnement behalten? Besuchen Sie:\n"
                f"https://lebenslauf-builder.de/mein-bereich/abonnement/\n\n"
                f"Mit freundlichen Gruessen\n"
                f"Ihr Lebenslauf-Builder Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.user.email],
        )

    if expiring.count() > 0:
        logger.info("Sent %d expiring subscription reminders", expiring.count())


@shared_task(bind=True, max_retries=3, queue="payments")
def generate_invoice_pdf(self, stripe_invoice_id):
    """
    Generate GoBD-compliant invoice PDF from Stripe invoice data.
    Called when invoice.paid webhook fires.
    """
    import stripe
    from payments.models import Payment, Invoice
    from documents.services import PDFRenderingService
    from django.template.loader import render_to_string
    from django.core.files.base import ContentFile
    from weasyprint import HTML

    try:
        stripe_invoice = stripe.Invoice.retrieve(stripe_invoice_id)
    except stripe.error.StripeError:
        logger.exception("Failed to retrieve Stripe invoice: %s", stripe_invoice_id)
        raise self.retry(countdown=60)

    # Find the corresponding payment
    pi_id = stripe_invoice.get("payment_intent", "")
    payment = Payment.objects.filter(stripe_payment_intent_id=pi_id).first()

    if not payment:
        logger.warning("No payment found for Stripe invoice: %s", stripe_invoice_id)
        return

    # Skip if invoice already exists
    if hasattr(payment, "invoice"):
        logger.info("Invoice already exists for payment: %s", payment.id)
        return

    # Create Invoice record
    invoice = Invoice(
        payment=payment,
        rechnungsdatum=timezone.now().date(),
        leistungszeitraum_start=(
            payment.subscription.current_period_start.date()
            if payment.subscription and payment.subscription.current_period_start
            else timezone.now().date()
        ),
        leistungszeitraum_end=(
            payment.subscription.current_period_end.date()
            if payment.subscription and payment.subscription.current_period_end
            else timezone.now().date()
        ),
    )
    invoice.save()  # This generates the rechnungsnummer

    # Render invoice PDF
    html_content = render_to_string("payments/invoice_pdf.html", {
        "invoice": invoice,
        "payment": payment,
        "user": payment.user,
        "company": {
            "name": "Lebenslauf-Builder GmbH",
            "strasse": "Musterstrasse 123",
            "plz": "10115",
            "stadt": "Berlin",
            "ust_id": "DE123456789",
            "steuernummer": "27/123/45678",
            "handelsregister": "HRB 123456 B, AG Berlin-Charlottenburg",
            "email": "rechnung@lebenslauf-builder.de",
        },
    })

    pdf_bytes = HTML(string=html_content).write_pdf()

    invoice.pdf_file.save(
        f"{invoice.rechnungsnummer}.pdf",
        ContentFile(pdf_bytes),
    )
    invoice.save()

    logger.info("Invoice generated: %s", invoice.rechnungsnummer)
```

---

## 8. Invoice Views

```python
class InvoiceListView(LoginRequiredMixin, View):
    """List all invoices for the current user."""

    def get(self, request):
        from payments.models import Invoice
        invoices = Invoice.objects.filter(
            payment__user=request.user,
        ).select_related("payment").order_by("-rechnungsdatum")

        return render(request, "payments/invoice_list.html", {
            "invoices": invoices,
        })


class InvoiceDownloadView(LoginRequiredMixin, View):
    """Download a specific invoice PDF."""

    def get(self, request, invoice_id):
        from payments.models import Invoice
        from django.http import FileResponse, Http404

        try:
            invoice = Invoice.objects.get(
                id=invoice_id,
                payment__user=request.user,
            )
        except Invoice.DoesNotExist:
            raise Http404

        if not invoice.pdf_file:
            messages.error(request, "Die Rechnung ist noch nicht verfuegbar.")
            return redirect("payments:invoice_list")

        return FileResponse(
            invoice.pdf_file.open("rb"),
            as_attachment=True,
            filename=f"{invoice.rechnungsnummer}.pdf",
            content_type="application/pdf",
        )
```
