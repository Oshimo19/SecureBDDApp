from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from accounts.models import User, DeletedUser

import json
import base64
import hmac
import hashlib
import time
import re


# JWT

def generate_jwt(payload, exp=3600):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload["exp"] = int(time.time()) + exp
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    to_sign = f"{header}.{payload_encoded}"
    signature = hmac.new(settings.SECRET_KEY.encode(), to_sign.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{to_sign}.{signature_encoded}"

def decode_jwt(token):
    try:
        header_b64, payload_b64, signature = token.split(".")
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        if not hmac.compare_digest(expected_sig_b64, signature):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


# Validation Regex de email et nom, prenom

def is_valid_email(email):
    return bool(re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))

def is_valid_name(name):
    return bool(re.fullmatch(r"^[A-Za-z\s\-']{1,100}$", name))

# Politique conforme ANSSI : 12+ caractères, maj, min, chiffre, caractere spécial
def is_strong_password(password):
    if not 12 <= len(password) <= 64:
        return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"\d", password): return False
    if not re.search(r"[^\w\s]", password): return False  # caracteres speciaux
    return True


# Vues REST securisees

@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request):
        try:
            data = getattr(request, "cleaned_data", None) or json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            firstName = data.get("firstName", "")
            lastName = data.get("lastName", "")
            role = data.get("role", "user")

            if not email or not password:
                return JsonResponse({"error": "Champs requis manquants"}, status=400)
            if not is_valid_email(email):
                return JsonResponse({"error": "Email invalide"}, status=400)
            if not is_strong_password(password):
                return JsonResponse({"error": "Mot de passe invalide"}, status=400)
            if not is_valid_name(firstName) or not is_valid_name(lastName):
                return JsonResponse({"error": "Nom ou prenom invalide"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email deja utilise"}, status=400)

            user = User.objects.create(
                email=email,
                password=make_password(password),
                firstName=firstName,
                lastName=lastName,
                role=role
            )
            return JsonResponse({"message": "Inscription reussie", "user_id": user.id})
        except Exception:
            return JsonResponse({"error": "Erreur serveur"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    def post(self, request):
        try:
            data = getattr(request, "cleaned_data", None) or json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Champs requis manquants"}, status=400)

            user = User.objects.filter(email=email).first()
            if not user or not check_password(password, user.password):
                return JsonResponse({"error": "Identifiants invalides"}, status=401)

            jwt_token = generate_jwt({"user_id": user.id, "role": user.role})
            return JsonResponse({"message": "Connexion reussie", "token": jwt_token})
        except Exception:
            return JsonResponse({"error": "Erreur serveur"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def post(self, request):
        return JsonResponse({"message": "Deconnexion reussie. Supprimez le token localement."})


class UserProfileView(View):
    def get(self, request):
        user = getattr(request, "user", None)
        if not user:
            return JsonResponse({"error": "Acces non autorise"}, status=401)
        return JsonResponse({
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "createdAt": user.createdAt,
        })


class AdminListUsersView(View):
    def get(self, request):
        user = getattr(request, "user", None)
        if not user or user.role != "admin":
            return JsonResponse({"error": "Acces refuse"}, status=403)
        users = User.objects.all().values("id", "email", "firstName", "lastName", "role", "createdAt")
        return JsonResponse({"users": list(users)})


@method_decorator(csrf_exempt, name="dispatch")
class AdminDeleteUserView(View):
    def post(self, request, user_id):
        user = getattr(request, "user", None)
        if not user or user.role != "admin":
            return JsonResponse({"error": "Acces refuse"}, status=403)
        try:
            target_user = User.objects.get(id=user_id)
            DeletedUser.objects.create(email=target_user.email, deletedBy=user)
            target_user.delete()
            return JsonResponse({"message": "Utilisateur supprime"})
        except User.DoesNotExist:
            return JsonResponse({"error": "Requete invalide"}, status=400)


class HomeView(View):
    def get(self, request):
        return JsonResponse({"message": "Bienvenue sur la page d accueil"})

