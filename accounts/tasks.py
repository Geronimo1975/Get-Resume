"""Celery tasks for async Brevo CRM contact sync."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def sync_brevo_contact_task(self, user_id):
    """Sync a newly registered user to Brevo CRM contacts."""
    from .models import User
    from .brevo import sync_contact_to_brevo

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("sync_brevo_contact_task: User %s not found", user_id)
        return

    sync_contact_to_brevo(user)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def update_brevo_contact_confirmed_task(self, user_id):
    """Update Brevo CRM contact after email confirmation."""
    from .models import User
    from .brevo import update_contact_confirmed

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("update_brevo_contact_confirmed_task: User %s not found", user_id)
        return

    update_contact_confirmed(user)
