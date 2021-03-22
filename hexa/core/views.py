from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.catalog.models import CatalogIndex, CatalogIndexType


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse("core:dashboard"))

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        next_url = request.POST["next"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect(next_url)
        else:
            errors = True
    else:
        errors = False
        next_url = request.GET.get("next", reverse("core:dashboard"))

    return render(request, "core/index.html", {"errors": errors, "next_url": next_url})


def dashboard(request):
    breadcrumbs = [(_("Dashboard"), "core:dashboard")]

    return render(
        request,
        "core/dashboard.html",
        {
            "counts": {
                "datasources": CatalogIndex.objects.filter(
                    index_type=CatalogIndexType.DATASOURCE
                )
                .for_user(request.user)
                .count()
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def ready(request):
    return HttpResponse("ok")
