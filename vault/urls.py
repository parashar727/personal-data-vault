from .views import index
from django.urls import path

urlpatterns = [
    path("", index.as_view(), name='index')
]