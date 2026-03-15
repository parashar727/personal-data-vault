from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
                status=400
            )

        encrypted_file = item.item_file

        if not encrypted_file:
            return Response(
                {"error": "File not found."},
                status=404
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