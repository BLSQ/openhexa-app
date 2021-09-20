from django.contrib.auth import authenticate, login
from django.db import connection
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.catalog.models import Index
from hexa.plugins.connector_s3.models import Object


def index(request: HttpRequest) -> HttpResponse:
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


def dashboard(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [(_("Dashboard"), "core:dashboard")]
    accessible_datasources = Index.objects.filter_for_user(request.user).roots()

    # TODO: We should instead filter on "executable file"-like on the index to avoid referencing a plugin here
    accessible_notebooks = Object.objects.filter(
        key__iendswith=".ipynb"
    ).filter_for_user(request.user)

    return render(
        request,
        "core/dashboard.html",
        {
            "counts": {
                "datasources": accessible_datasources.count(),
                "notebooks": accessible_notebooks.count(),
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def ready(request: HttpRequest) -> HttpResponse:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            expected = (1,)
            if row != expected:
                return HttpResponseServerError(
                    f"Error: invalid database response (is `{row}`, should be `{expected}`)"
                )
    except Exception as e:
        return HttpResponseServerError(f"Error: can not connect to the database ({e})")

    return HttpResponse("ok")
