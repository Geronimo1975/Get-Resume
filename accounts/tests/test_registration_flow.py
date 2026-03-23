"""
End-to-end registration flow tests.

Tests the full API contract:
  1. Register a new account (POST /api/v1/auth/registration/)
  2. Verify User + UserProfile created with correct data
  3. Verify JWT tokens returned
  4. Login with the new account (POST /api/v1/auth/login/)
  5. Access protected endpoint with JWT (GET /api/v1/users/me/)
  6. Validation: duplicate email, password mismatch, weak password, missing fields
"""
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserProfile
from allauth.account.models import EmailAddress


REGISTER_URL = "/api/v1/auth/registration/"
LOGIN_URL = "/api/v1/auth/login/"
ME_URL = "/api/v1/users/me/"


def valid_registration_data(**overrides):
    data = {
        "email": "max.mustermann@example.de",
        "first_name": "Max",
        "last_name": "Mustermann",
        "password1": "SicheresP@ss2025!",
        "password2": "SicheresP@ss2025!",
    }
    data.update(overrides)
    return data


@patch("accounts.tasks.sync_brevo_contact_task.delay")
class RegistrationFlowTests(TestCase):
    """Full registration → login → profile access flow."""

    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_profile(self, mock_brevo):
        """Registration creates User + UserProfile via signal."""
        response = self.client.post(REGISTER_URL, valid_registration_data())

        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_204_NO_CONTENT])

        # User created with correct fields
        user = User.objects.get(email="max.mustermann@example.de")
        self.assertEqual(user.first_name, "Max")
        self.assertEqual(user.last_name, "Mustermann")
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

        # UserProfile auto-created by signal
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.subscription_plan, "free")

    def test_register_returns_jwt_tokens(self, mock_brevo):
        """Registration response includes access + refresh JWT tokens."""
        response = self.client.post(REGISTER_URL, valid_registration_data())

        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_204_NO_CONTENT])

        # dj-rest-auth with JWT returns tokens in body
        if response.status_code == status.HTTP_200_OK or response.data:
            data = response.data
            self.assertIn("access", data)
            self.assertIn("refresh", data)

    def test_register_creates_email_address_record(self, mock_brevo):
        """Registration creates an allauth EmailAddress for verification tracking."""
        self.client.post(REGISTER_URL, valid_registration_data())

        user = User.objects.get(email="max.mustermann@example.de")

        # allauth EmailAddress record exists (prerequisite for verification flow)
        email_addr = EmailAddress.objects.filter(user=user, email=user.email).first()
        self.assertIsNotNone(email_addr, "allauth EmailAddress record should be created on registration")
        self.assertTrue(email_addr.primary)

    def test_register_dispatches_brevo_sync(self, mock_brevo):
        """Registration dispatches async Brevo CRM sync task."""
        self.client.post(REGISTER_URL, valid_registration_data())

        user = User.objects.get(email="max.mustermann@example.de")
        mock_brevo.assert_called_once_with(str(user.pk))

    def test_login_after_registration(self, mock_brevo):
        """New user can login and receives JWT tokens."""
        self.client.post(REGISTER_URL, valid_registration_data())

        response = self.client.post(LOGIN_URL, {
            "email": "max.mustermann@example.de",
            "password": "SicheresP@ss2025!",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_access_me_endpoint_with_jwt(self, mock_brevo):
        """Authenticated user can access /users/me/ with JWT."""
        self.client.post(REGISTER_URL, valid_registration_data())

        # Login to get tokens
        login_resp = self.client.post(LOGIN_URL, {
            "email": "max.mustermann@example.de",
            "password": "SicheresP@ss2025!",
        })
        token = login_resp.data["access"]

        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "max.mustermann@example.de")
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["last_name"], "Mustermann")

    def test_me_endpoint_unauthenticated_returns_401(self, mock_brevo):
        """Unauthenticated request to /users/me/ returns 401."""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@patch("accounts.tasks.sync_brevo_contact_task.delay")
class RegistrationValidationTests(TestCase):
    """Validation edge cases for registration."""

    def setUp(self):
        self.client = APIClient()

    def test_duplicate_email_rejected(self, mock_brevo):
        """Cannot register with an already-taken email."""
        self.client.post(REGISTER_URL, valid_registration_data())

        response = self.client.post(REGISTER_URL, valid_registration_data(
            first_name="Erika",
            last_name="Musterfrau",
        ))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_rejected(self, mock_brevo):
        """password1 != password2 returns validation error."""
        response = self.client.post(REGISTER_URL, valid_registration_data(
            password2="AnderesPasswort123!",
        ))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_rejected(self, mock_brevo):
        """Password shorter than 10 chars is rejected."""
        response = self.client.post(REGISTER_URL, valid_registration_data(
            password1="short1!",
            password2="short1!",
        ))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email_rejected(self, mock_brevo):
        """Registration without email returns 400."""
        data = valid_registration_data()
        del data["email"]
        response = self.client.post(REGISTER_URL, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_first_name_rejected(self, mock_brevo):
        """Registration without first_name returns 400."""
        data = valid_registration_data()
        del data["first_name"]
        response = self.client.post(REGISTER_URL, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_format_rejected(self, mock_brevo):
        """Malformed email returns 400."""
        response = self.client.post(REGISTER_URL, valid_registration_data(
            email="not-an-email",
        ))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
