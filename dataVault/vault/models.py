
from django.db import models
from django.db.models import ForeignKey
from django.conf import settings
from django.utils import timezone


# Create your models here.
class SoftDeleteManager(models.Manager):
    # Overrides default get_queryset to exclude soft deleted objects
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Vault(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vaults")

    name = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeleteManager()

    # Use this to get all objects (including soft deleted)
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.items.all().update(deleted_at=self.deleted_at)
        self.save()

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

    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeleteManager()

    # Use this to get all objects (including soft deleted)
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        """
        if self.item_file:
            self.item_file.delete(save=False)
        super().delete(*args, **kwargs)
        """
        self.deleted_at = timezone.now()
        self.save()