from django.conf import settings
from django.shortcuts import render
from django import get_version
import os

def home(request):
    context = {
        "debug": settings.DEBUG,
        "django_ver": get_version(),
        "python_ver": os.environ.get("PYTHON_VERSION", "Unknown"),
    }
    return render(request, "home/main.html", context)

def learning(request):
    return render(request, "home/learning.html")
