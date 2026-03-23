"""
Custom allauth adapter that redirects confirmation/reset URLs
to the Vue SPA frontend instead of Django templates.
"""

from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Return a frontend URL for email confirmation.

        Default allauth returns a Django view URL, but our frontend
        is a Vue SPA that handles confirmation via API call.
        """
        return f"{settings.FRONTEND_URL}/email-bestaetigen/{emailconfirmation.key}/"

    def send_mail(self, template_prefix, email, context):
        """
        Inject FRONTEND_URL into email template context so templates
        can reference it for links.
        """
        context["frontend_url"] = settings.FRONTEND_URL
        return super().send_mail(template_prefix, email, context)
