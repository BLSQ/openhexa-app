from django.shortcuts import render

from .models import *


def index(request):
    return render(request, "catalog/index.html", {"page_title": "Catalog"})
