import json

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from .models import AdminAccount, OrganizerAccount, OrganizerProfile, UserAccount


class AuthRegistrationTests(TestCase):
    def post_register(self, payload):
        return self.client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_register_user_by_default(self):
        response = self.post_register(
            {
                "full_name": "Иван Петров",
                "login": "parent@example.com",
                "password": "secret123",
            }
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["user"]["role"], "user")
        self.assertTrue(UserAccount.objects.filter(email="parent@example.com").exists())

    def test_register_organizer_creates_account_and_profile(self):
        response = self.post_register(
            {
                "full_name": "Театр Солнце",
                "login": "org@example.com",
                "password": "secret123",
                "user_type": "organizer",
            }
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["user"]["role"], "organizer")

        organizer = OrganizerAccount.objects.get(email="org@example.com")
        profile = OrganizerProfile.objects.get(organizer_account=organizer)
        self.assertEqual(profile.display_name, "Театр Солнце")
        self.assertEqual(profile.contact_person, "Театр Солнце")

    def test_register_organizer_requires_email_login(self):
        response = self.post_register(
            {
                "full_name": "Театр Солнце",
                "login": "+79990000000",
                "password": "secret123",
                "user_type": "organizer",
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(OrganizerAccount.objects.exists())

    def test_register_rejects_existing_admin_login(self):
        AdminAccount.objects.create(
            email="admin",
            password_hash=make_password("admin"),
            status=AdminAccount.STATUS_ACTIVE,
        )

        response = self.post_register(
            {
                "full_name": "Иван Петров",
                "login": "admin",
                "password": "secret123",
            }
        )

        self.assertEqual(response.status_code, 409)
        self.assertFalse(UserAccount.objects.exists())
