from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from vault.models import Vault, VaultItem
from vault.serializers import VaultSerializer, VaultItemSerializer


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
