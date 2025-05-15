from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from django.contrib.auth.hashers import make_password
import json

# Create your tests here.

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Creation d un utilisateur admin (avec prenom et nom facultatifs)
        self.admin_user = User.objects.create(
        email="admin@test.com",
        password=make_password("admin123"),
        firstName="",
        lastName="",
        role="admin"
        )

        # Creation d un utilisateur standard
        self.standard_user = User.objects.create(
            email="user1@test.com",
            password=make_password("user123"),
            firstName="",
            lastName="",
            role="user"
    )

    def test_home_page(self):
        """
        Test de la page publique d'accueil
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bienvenue", response.json().get("message", ""))

    def test_register_success(self):
        """
        Test d'inscription d'un nouvel utilisateur
        """
        data = {
            "email": "user2@test.com",
            "password": "user456",
            "firstName": "Alice",
            "lastName": "Bob"
        }
        response = self.client.post(
            reverse("register"),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Inscription reussie", response.json().get("message", ""))

    def test_login_success(self):
        """
        Test de connexion avec bon mot de passe
        """
        data = {"email": "user1@test.com", "password": "user123"}
        response = self.client.post(
            reverse("login"),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200, f"Réponse : {response.content}")
        self.assertIn("token", response.json())

    def test_login_failure(self):
        """
        Test de connexion avec mot de passe incorrect
        """
        data = {"email": "user1@test.com", "password": "wrongPassword"}
        response = self.client.post(
            reverse("login"),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Mot de passe incorrect", response.json().get("error", ""))

    def test_duplicate_register(self):
        """
        Test d'inscription avec email deja existant
        """
        data = {
            "email": "user1@test.com",  # deja utilise
            "password": "whatever"
        }
        response = self.client.post(
            reverse("register"),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email deja utilise", response.json().get("error", ""))
