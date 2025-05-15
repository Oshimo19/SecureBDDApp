import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement du fichier .env
load_dotenv()

# Repertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Cle secrete
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("[-] DJANGO_SECRET_KEY manquant dans .env")

# Mode debug et hotes autorises
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Applications installees
INSTALLED_APPS = [
    "accounts",
]

# Middleware utilise (minimise pour API)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "accounts.middleware.JWTMiddleware",
]

# Pas de templates utilises
TEMPLATES = []

# Pas de session, pas d admin
AUTH_PASSWORD_VALIDATORS = []

# Hachage securise avec Argon2id (active via make_password + PASSWORD_HASHERS)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# Configuration base de donnees PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "securebdd-db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# Localisation
LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "fr-fr")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = False
USE_TZ = True

# Pas de fichiers statiques ni d interface
STATIC_URL = None

# Champ ID par defaut
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Pas d admin, pas de WSGI si tu ne déploies pas avec gunicorn
WSGI_APPLICATION = "secureBDDApp.wsgi.application"
