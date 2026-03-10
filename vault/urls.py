from rest_framework.routers import DefaultRouter
from .views import VaultViewSet, VaultItemViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'vaults', VaultViewSet, basename="vault")
router.register(r'items', VaultItemViewSet, basename="vaultitem")

urlpatterns = [
    path('', include(router.urls))
]