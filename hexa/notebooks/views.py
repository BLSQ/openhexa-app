from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, "notebooks/index.html")


def run(request):
    return render(
        request, "notebooks/run.html", {"notebooks_url": settings.NOTEBOOKS_URL}
    )
