from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from vault.models import Vault, VaultItem
from vault.serializers import VaultSerializer, VaultItemSerializer
from vault.services.file_encryption import decrypt_file


# Create your views here.

class VaultViewSet(ModelViewSet):
    serializer_class = VaultSerializer
    permission_classes = [IsAuthenticated]
    queryset = Vault.objects.all()

    def get_queryset(self):
        return Vault.objects.filter(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        deleted_vault = Vault.all_objects.filter(owner=request.user, pk=pk).first()

        if not deleted_vault:
            return Response(
                {"detail": "Vault not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if deleted_vault.deleted_at is None:
            return Response(
                {"detail": "Vault is not currently deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_time = deleted_vault.deleted_at

        deleted_vault.deleted_at = None
        deleted_vault.save()

        # Use all_objects manager because default manager will only return non deleted items
        VaultItem.all_objects.filter(vault=deleted_vault, deleted_at=deleted_time).update(deleted_at=None)

        return Response(
            {"detail": "Vault and its items restored successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def trash(self, request):
        """
        Returns list of all soft-deleted vaults that belong to the user
        """
        deleted_vaults = Vault.all_objects.filter(owner=request.user, deleted_at__isnull=False)

        serializer = self.get_serializer(deleted_vaults, many=True)
        return Response(serializer.data)


class VaultItemViewSet(ModelViewSet):
    serializer_class = VaultItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = VaultItem.objects.all()

    def get_queryset(self):
        return VaultItem.objects.filter(vault__owner=self.request.user)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        item = self.get_object()

        if item.item_type != "DOC":
            return Response(
                {"error": "This item does not contain a downloadable file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        encrypted_file = item.item_file

        if not encrypted_file:
            return Response(
                {"error": "File not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        encrypted_bytes = encrypted_file.read()

        decrypted_bytes = decrypt_file(encrypted_bytes)

        response = HttpResponse(
            decrypted_bytes,
            content_type=item.metadata.get("content_type", "application/octet-stream")
        )

        filename = item.metadata.get("original_name", "downloaded_file")

        response["Content-Disposition"] = f'attachment; filename={filename}'

        return response

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        deleted_item = VaultItem.all_objects.filter(vault__owner=request.user, pk=pk).first()

        if not deleted_item:
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        if deleted_item.deleted_at is None:
            return Response(
                {"detail": "Item is not currently deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_item.deleted_at = None
        deleted_item.save()

        return Response(
            {"detail": "Item restored successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"])
    def trash(self, request):
        """
        Returns list of all soft-deleted items that belong to the user
        """
        deleted_items = VaultItem.all_objects.filter(vault__owner=request.user, deleted_at__isnull=False)

        serializer = self.get_serializer(deleted_items, many=True)
        return Response(serializer.data)