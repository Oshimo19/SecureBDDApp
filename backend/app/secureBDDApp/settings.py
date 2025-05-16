import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement des variables d environnement (.env)
load_dotenv()

# Repertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Cle secrete
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("[-] DJANGO_SECRET_KEY manquant dans .env")

# Mode debug et liste des hotes autorises
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Applications installees (API uniquement)
INSTALLED_APPS = [
    "accounts", # Appli principale
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",             # En-tetes de securite HTTP
    "django.middleware.common.CommonMiddleware",                 # Reponses compatibles HTTP standards
    "accounts.middleware.JWTMiddleware",                         # Authentification JWT
    "accounts.middleware.BruteForceProtectionMiddleware",        # Protection brute force
    "accounts.middleware.SecureIDORMiddleware",                  # Contre les acces illegitimes
    "accounts.middleware.ErrorHandlingMiddleware",               # Erreurs unifiees
]

# Aucun moteur de templates necessaire (API uniquement)
TEMPLATES = []

# Pas d admin ni de sessions classiques
AUTH_PASSWORD_VALIDATORS = []

# Routing principal
ROOT_URLCONF = "secureBDDApp.urls"

# Algo de hachage securise (Argon2id)
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

# Localisation et fuseau horaire
LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "fr-fr")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = False
USE_TZ = True

# Pas de fichiers statiques exposes
STATIC_URL = None

# ID auto par defaut pour les tables
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Application WSGI (necessaire meme si gunicorn n est pas encore configure)
WSGI_APPLICATION = "secureBDDApp.wsgi.application"
