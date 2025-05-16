from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin
from accounts.models import User

import base64
import hashlib
import hmac
import json
import time
import logging
from html import escape


# Logs de securite
logger = logging.getLogger(__name__)


# Middleware JWT - Authentifier l utilisateur via un token signe
class JWTMiddleware(MiddlewareMixin):
    # Recuperer le token JWT via en tete "Authorization: Bearer ..."
    def process_request(self, request):
        request.user = None
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ")[1]
            payload = self.decode_jwt(token)
            if payload and "user_id" in payload:
                try:
                    request.user = User.objects.get(id=payload["user_id"])
                except User.DoesNotExist:
                    logger.warning("[JWT] Utilisateur non trouve")

    # Decoder le token JWT
    def decode_jwt(self, token):
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            message = f"{header_b64}.{payload_b64}"
            expected_sig = self.sign(message)

            if not hmac.compare_digest(signature_b64, expected_sig):
                logger.warning("[JWT] Signature invalide")
                return None

            payload_json = base64.urlsafe_b64decode(payload_b64 + "==")
            return json.loads(payload_json)
        
        except Exception:
            logger.warning("[JWT] Token malforme")
            return None

    # Signer le message avec algo SHA256
    def sign(self, message: str) -> str:
        secret = settings.SECRET_KEY.encode()
        sig = hmac.new(secret, message.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(sig).decode().rstrip("=")


# Middleware anti-bruteforce avec nettoyage des champs (Sanitizing)
class BruteForceProtectionMiddleware(MiddlewareMixin):
    MAX_ATTEMPTS = 5        # nb de tentative echoue max, ici 5
    BLOCK_DURATION = 300    # temps de blocage en secondes, ici 300 s = 5 min

    # Protecter les routes login et register
    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path.lower()
        if path.endswith("/register/") or path.endswith("/login/"):
            try:
                data = json.loads(request.body)
            except Exception:
                return JsonResponse({"error": "Requete invalide"}, status=400)

            # Nettoyage des champs pour eviter injections de type XSS (Sanitizing)
            request.cleaned_data = {
                "email": escape(data.get("email", "").strip().lower()),
                "password": escape(data.get("password", "")),
                "firstName": escape(data.get("firstName", "")),
                "lastName": escape(data.get("lastName", "")),
            }
            request.cleaned_email = request.cleaned_data["email"]

            # Blocker par IP si brute force avec trop de tentatvies ecouhees
            ip = self.get_client_ip(request)

            if self.is_blocked(request.cleaned_email, ip):
                logger.warning(f"[BRUTEFORCE] Blocage IP/email : {ip} / {request.cleaned_email}")
                return JsonResponse({"error": "Trop de tentatives. Reessayez plus tard."}, status=429)

        return None

    # Enregistrer les echecs d authentification
    def process_response(self, request, response):
        if request.path.endswith("/login/") and response.status_code == 401:
            email = getattr(request, "cleaned_email", None)
            ip = self.get_client_ip(request)
            if email and ip:
                self.increment_failure(email, ip)
                logger.info(f"[ECHEC LOGIN] IP: {ip} - Email: {email}")
        return response

    # Recupere l IP du client
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    # Verifie si l email ou l IP est bloque
    def is_blocked(self, email, ip):
        for key in [f"fail:{email}", f"fail:{ip}"]:
            fail_data = cache.get(key, {"count": 0, "until": 0})
            if fail_data["count"] >= self.MAX_ATTEMPTS and time.time() < fail_data["until"]:
                return True
        return False

    # Incremente les echecs et applique blocage si besoin
    def increment_failure(self, email, ip):
        for key in [f"fail:{email}", f"fail:{ip}"]:
            fail_data = cache.get(key, {"count": 0, "until": 0})
            fail_data["count"] += 1
            if fail_data["count"] >= self.MAX_ATTEMPTS:
                fail_data["until"] = time.time() + self.BLOCK_DURATION
            cache.set(key, fail_data, timeout=self.BLOCK_DURATION)


# Middleware contre IDOR et acces admin non autorise
class SecureIDORMiddleware(MiddlewareMixin):
    # Applique un controle d acces avant la vue
    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path
        user = getattr(request, "user", None)

        if user and getattr(user, "id", None):
            # Controle des routes admin
            if path.startswith("/api/admin") and user.role != "admin":
                logger.warning(f"[SECURITE] Tentative acces admin refuse pour user {user.email}")
                return HttpResponseForbidden("Acces refuse")

            # Controle IDOR : Bloque l acces d un utilisateur a un autre profil que soi (ex: /api/user/5/)
            if path.startswith("/api/user/"):
                segments = path.rstrip("/").split("/")
                if segments[-1].isdigit() and int(segments[-1]) != user.id:
                    logger.warning(f"[IDOR] User {user.email} tente d acceder a user {segments[-1]}")
                    return HttpResponseBadRequest("Requete invalide")

        return None


# Middleware pour erreur uniforme sur routes invalides
class ErrorHandlingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Ne remplace que si le corps est vide
        if response.status_code in (400, 403, 404, 500):
            try:
                content = json.loads(response.content)
            except Exception:
                content = {}

            if "error" not in content:
                logger.warning(f"[ERREUR HTTP {response.status_code}] pour {request.path}")
                return JsonResponse({"error": "Acces interdit ou ressource introuvable"}, status=response.status_code)

        return response
