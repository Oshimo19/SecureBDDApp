from django.test import TestCase, Client, override_settings
from django.urls import reverse
from accounts.models import User, DeletedUser
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
import json

@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class AccountsTestCase(TestCase):
    def setUp(self):
        cache.clear()  # Reset middleware state
        self.client = Client()

        self.admin_user = User.objects.create(
            email="admin@test.com",
            password=make_password("Admin123!Test"),
            role="admin"
        )

        self.standard_user = User.objects.create(
            email="user@test.com",
            password=make_password("User123!Test"),
            role="user"
        )

    def get_token(self, email, password):
        response = self.client.post(reverse("login"), data=json.dumps({
            "email": email,
            "password": password
        }), content_type="application/json")
        return response.json().get("token")

    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bienvenue", response.json().get("message", ""))

    def test_register_success(self):
        data = {
            "email": "test@example.com",
            "password": "StrongPwd123!",
            "firstName": "Alice",
            "lastName": "Bob"
        }
        response = self.client.post(reverse("register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Inscription reussie", response.json().get("message", ""))

    def test_register_invalid_email(self):
        data = {
            "email": "invalid-email<script>",
            "password": "StrongPwd123!",
            "firstName": "Alice",
            "lastName": "Bob"
        }
        response = self.client.post(reverse("register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email invalide", response.json().get("error", ""))

    def test_register_weak_password(self):
        data = {
            "email": "weakpass@example.com",
            "password": "123",
            "firstName": "Alice",
            "lastName": "Bob"
        }
        response = self.client.post(reverse("register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Mot de passe invalide", response.json().get("error", ""))

    def test_register_duplicate_email(self):
        data = {
            "email": "user@test.com",
            "password": "StrongPwd123!",
            "firstName": "Alice",
            "lastName": "Dupont"
        }
        response = self.client.post(reverse("register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email deja utilise", response.json().get("error", ""))

    def test_login_success(self):
        data = {"email": "user@test.com", "password": "User123!Test"}
        response = self.client.post(reverse("login"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_invalid_credentials(self):
        data = {"email": "user@test.com", "password": "wrong"}
        response = self.client.post(reverse("login"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Identifiants invalides", response.json().get("error", ""))

    def test_user_profile_unauthenticated(self):
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, 401)
        self.assertIn("Acces non autorise", response.json().get("error", ""))

    def test_admin_access_denied_to_user(self):
        token = self.get_token("user@test.com", "User123!Test")
        response = self.client.get(reverse("admin-users"), HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, 403)
        self.assertIn("Acces interdit", response.json().get("error", ""))

    def test_admin_delete_user_success(self):
        token = self.get_token("admin@test.com", "Admin123!Test")
        target = User.objects.create(
            email="victime@test.com",
            password=make_password("Test1234567!"),
            role="user"
        )
        response = self.client.post(
            reverse("admin-delete-user", args=[target.id]),
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Utilisateur supprime", response.json().get("message", ""))
        self.assertFalse(User.objects.filter(id=target.id).exists())
        self.assertTrue(DeletedUser.objects.filter(email="victime@test.com").exists())

    def test_bruteforce_blocking(self):
        email = "user@test.com"
        for i in range(6):
            data = {"email": email, "password": "Wrong123!"}
            self.client.post(reverse("login"), data=json.dumps(data), content_type="application/json")
        response = self.client.post(reverse("login"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 429)
        self.assertIn("Trop de tentatives", response.json().get("error", ""))

    def test_xss_payload_in_name(self):
        data = {
            "email": "xss@example.com",
            "password": "StrongPwd123!",
            "firstName": "<script>alert(1)</script>",
            "lastName": "Bob"
        }
        response = self.client.post(reverse("register"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Nom ou prenom invalide", response.json().get("error", ""))

    def test_invalid_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Acces interdit", response.json().get("error", ""))
