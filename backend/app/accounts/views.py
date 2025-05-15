from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password

import json
import base64
import hmac
import hashlib
import time

from accounts.models import User, DeletedUser

# --- Fonctions JWT ---

def generate_jwt(payload: dict, exp: int = 3600) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload["exp"] = int(time.time()) + exp
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    to_sign = f"{header}.{payload_encoded}"
    signature = hmac.new(settings.SECRET_KEY.encode(), to_sign.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{to_sign}.{signature_encoded}"

def decode_jwt(token: str) -> dict:
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


# --- Vues ---

@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            firstName = data.get("firstName", "")
            lastName = data.get("lastName", "")
            role = data.get("role", "user")

            if not email or not password:
                return JsonResponse({"error": "Email et mot de passe requis"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email deja utilise"}, status=400)

            user = User.objects.create(
                email=email,
                password=make_password(password),
                firstName=firstName,
                lastName=lastName,
                role=role,
            )

            return JsonResponse({"message": "Inscription reussie", "user_id": user.id})
        except Exception:
            return JsonResponse({"error": "Erreur serveur"}, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "Email et mot de passe requis"}, status=400)

            user = User.objects.get(email=email)
            if not check_password(password, user.password):
                return JsonResponse({"error": "Mot de passe incorrect"}, status=401)

            jwt_token = generate_jwt({"user_id": user.id, "role": user.role})
            return JsonResponse({"message": "Connexion reussie", "token": jwt_token})

        except User.DoesNotExist:
            return JsonResponse({"error": "Utilisateur introuvable"}, status=404)
        except Exception:
            return JsonResponse({"error": "Erreur serveur"}, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def post(self, request):
        return JsonResponse({"message": "Deconnexion reussie. Supprimez le token localement."})

class UserProfileView(View):
    def get(self, request):
        if not request.user:
            return JsonResponse({"error": "Non authentifie"}, status=401)

        user = request.user
        return JsonResponse({
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "createdAt": user.createdAt,
        })

class AdminListUsersView(View):
    def get(self, request):
        if not request.user or request.user.role != "admin":
            return JsonResponse({"error": "Acces refuse"}, status=403)

        users = User.objects.all().values("id", "email", "firstName", "lastName", "role", "createdAt")
        return JsonResponse({"users": list(users)})

@method_decorator(csrf_exempt, name="dispatch")
class AdminDeleteUserView(View):
    def post(self, request, user_id):
        if not request.user or request.user.role != "admin":
            return JsonResponse({"error": "Acces refuse"}, status=403)

        try:
            user = User.objects.get(id=user_id)
            DeletedUser.objects.create(email=user.email, deletedBy=request.user)
            user.delete()
            return JsonResponse({"message": "Utilisateur supprime"})
        except User.DoesNotExist:
            return JsonResponse({"error": "Utilisateur introuvable"}, status=404)

class HomeView(View):
    def get(self, request):
        return JsonResponse({"message": "Bienvenue sur la page d accueil"})
