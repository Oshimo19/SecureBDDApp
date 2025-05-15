import base64
import hashlib
import hmac
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from accounts.models import User

class JWTMiddleware(MiddlewareMixin):
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
                    pass

    def decode_jwt(self, token: str):
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            message = f"{header_b64}.{payload_b64}"
            expected_sig = self.sign(message)

            if not hmac.compare_digest(signature_b64, expected_sig):
                return None

            payload_json = base64.urlsafe_b64decode(payload_b64 + "==")
            return json.loads(payload_json)
        except Exception:
            return None

    def sign(self, message: str) -> str:
        secret = settings.SECRET_KEY.encode()
        sig = hmac.new(secret, message.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(sig).decode().rstrip("=")
