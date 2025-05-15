import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement du .env
load_dotenv()

# Repertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Securite de la cle secret
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("[-] DJANGO_SECRET_KEY est manquant dans .env")

# Debug & hotes autorises
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Applications installees
INSTALLED_APPS = [
    'accounts',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'accounts.middleware.JWTMiddleware',
]

ROOT_URLCONF = 'secureBDDApp.urls'

# Templates
TEMPLATES = []

WSGI_APPLICATION = 'secureBDDApp.wsgi.application'

# Base de donnees PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("POSTGRES_DB"),
        'USER': os.getenv("POSTGRES_USER"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'HOST': os.getenv("POSTGRES_HOST", "pgsdb"),
        'PORT': os.getenv("POSTGRES_PORT", "5432"),
    }
}

# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = []

# Hachage des mots de passe (Argon2id)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# Localisation
LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "fr-fr")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = 'static/'

# Champ ID auto par defaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
