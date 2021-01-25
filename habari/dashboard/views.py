from django.shortcuts import render

from .models import *


def index(request):
    breadcrumbs = [("Dashboard", "dashboard:index")]
    stats = {s.code: s.value for s in Stat.objects.all()}

    return render(
        request, "dashboard/index.html", {"stats": stats, "breadcrumbs": breadcrumbs}
    )
