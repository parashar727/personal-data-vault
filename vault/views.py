from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.

class index(APIView):

    def get(self, request):
        return Response("Vault works")
