"""
Brevo CRM contact sync service.

Syncs user data to Brevo contacts on registration and email confirmation.
Uses the official sib-api-v3-sdk (Brevo Python SDK).
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _get_contacts_api():
    """Lazily initialise the Brevo ContactsApi client."""
    import sib_api_v3_sdk

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY
    return sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))


def sync_contact_to_brevo(user):
    """
    Create or update a Brevo CRM contact for the given user.

    Attributes synced: FIRSTNAME, LASTNAME, REGISTRATION_DATE,
    EMAIL_CONFIRMED, SUBSCRIPTION_PLAN.

    Uses update_enabled=True so this is idempotent — calling it for
    an existing contact simply updates the attributes.
    """
    import sib_api_v3_sdk

    if not settings.BREVO_API_KEY:
        logger.debug("BREVO_API_KEY not set, skipping contact sync")
        return

    api = _get_contacts_api()

    subscription_plan = "free"
    if hasattr(user, "profile"):
        subscription_plan = user.profile.subscription_plan

    attributes = {
        "FIRSTNAME": user.first_name or "",
        "LASTNAME": user.last_name or "",
        "REGISTRATION_DATE": user.date_joined.strftime("%Y-%m-%d"),
        "EMAIL_CONFIRMED": user.is_email_verified,
        "SUBSCRIPTION_PLAN": subscription_plan,
    }

    try:
        contact = sib_api_v3_sdk.CreateContact(
            email=user.email,
            attributes=attributes,
            update_enabled=True,
        )
        api.create_contact(contact)
        logger.info("Brevo contact synced: %s", user.email)
    except sib_api_v3_sdk.rest.ApiException as e:
        logger.error("Brevo API error syncing %s: %s", user.email, e)
        raise


def update_contact_confirmed(user):
    """
    Update a Brevo contact to mark email as confirmed.

    Called after the user clicks the email confirmation link.
    """
    import sib_api_v3_sdk

    if not settings.BREVO_API_KEY:
        logger.debug("BREVO_API_KEY not set, skipping confirmation update")
        return

    api = _get_contacts_api()

    from django.utils import timezone

    attributes = {
        "EMAIL_CONFIRMED": True,
        "CONFIRMED_AT": timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    try:
        contact = sib_api_v3_sdk.UpdateContact(attributes=attributes)
        api.update_contact(user.email, contact)
        logger.info("Brevo contact confirmed: %s", user.email)
    except sib_api_v3_sdk.rest.ApiException as e:
        logger.error("Brevo API error confirming %s: %s", user.email, e)
        raise
