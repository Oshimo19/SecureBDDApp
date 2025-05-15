import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "secureBDDApp.settings")
django.setup()

from accounts.models import User
from django.contrib.auth.hashers import make_password

User.objects.create(
    email="test@example.com",
    password=make_password("secretpass"),
    role="user"
)
