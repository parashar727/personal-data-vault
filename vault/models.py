from django.db import models
from django.db.models import ForeignKey
from django.conf import settings


# Create your models here.

class Vault(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vaults")

    name = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VaultItem(models.Model):
    vault = models.ForeignKey(Vault, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=100)

    ITEM_CHOICES = [
        ("LOG", "Login"),
        ("NOT", "Note"),
        ("DOC", "Document"),
    ]

    item_type = models.CharField(max_length=3, choices=ITEM_CHOICES, default="LOG")

    encrypted_data = models.TextField()

    item_file = models.FileField(upload_to="vault_files/", null=True, blank=True)

    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.item_file:
            self.item_file.delete(save=False)
        super().delete(*args, **kwargs)
