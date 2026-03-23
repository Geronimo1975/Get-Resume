import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile

logger = logging.getLogger(__name__)


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


@receiver(post_save, sender=User)
def sync_new_user_to_brevo(sender, instance, created, **kwargs):
    """Dispatch Celery task to sync new user to Brevo CRM."""
    if created:
        from .tasks import sync_brevo_contact_task

        sync_brevo_contact_task.delay(str(instance.pk))
        logger.info("Brevo sync dispatched for new user: %s", instance.email)


def handle_email_confirmed(sender, request, email_address, **kwargs):
    """
    Called when allauth confirms an email address.
    Updates User.is_email_verified and syncs to Brevo CRM.
    """
    user = email_address.user
    if not user.is_email_verified:
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

    from .tasks import update_brevo_contact_confirmed_task

    update_brevo_contact_confirmed_task.delay(str(user.pk))
    logger.info("Brevo confirmation sync dispatched for: %s", user.email)


# Connect to allauth's email_confirmed signal
try:
    from allauth.account.signals import email_confirmed

    email_confirmed.connect(handle_email_confirmed)
except ImportError:
    pass
