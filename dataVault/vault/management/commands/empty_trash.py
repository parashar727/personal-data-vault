from django.core.management.base import BaseCommand
from django.utils import timezone

from vault.models import Vault, VaultItem
from datetime import timedelta

class Command(BaseCommand):
    help = "Permanently removes all soft deleted objects past a certain date."

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help="Delete items soft-deleted more than this many days ago")

    def handle(self, *args, **options):
        days = options['days']

        cutoff = timezone.now() - timedelta(days=days)

        deleted_items = VaultItem.all_objects.filter(deleted_at__lte=cutoff)
        item_count = deleted_items.count()

        if item_count > 0:
            self.stdout.write(f"Found {item_count} soft-deleted items. Cleaning up...")

            for item in deleted_items:
                if item.item_file:
                    self.stdout.write(f"Deleting {item.item_file.name}")
                    item.item_file.delete(save=False)

            deleted_items.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {item_count} items."))
        else:
            self.stdout.write("Found no soft-deleted items.")

        deleted_vaults = Vault.all_objects.filter(deleted_at__lte=cutoff)
        vault_count = deleted_vaults.count()

        if vault_count > 0:
            deleted_vaults.delete()
            self.stdout.write(f"Successfully deleted {vault_count} vaults.")
        else:
            self.stdout.write("Found no soft-deleted vaults")