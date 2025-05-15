from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

# Utilisateur (Table users)
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=255)
    firstName = models.CharField(max_length=100, blank=True, null=True)
    lastName  = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES)
    createdAt = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Si password est en clair, on le hache avec Argon2id
        if not self.password.startswith("argon2"):
            self.password = make_password(self.password)    # utilise Argon2id selon settings.py
        super().save(*args, **kwargs)

    def get_masked_password(self):
        return "*****"

    def __str__(self):
        return f"{self.email} ({self.role})"

# Journal de suppression (Table deletedUsers)
class DeletedUser(models.Model):
    email = models.EmailField(max_length=254, blank=True)
    deletedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deleted_users")
    deletedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email or 'Utilisateur inconnu'} supprime par {self.deletedBy.email}"
