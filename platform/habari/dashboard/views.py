from django.shortcuts import render

from .models import *


def index(request):
    stats = {s.code: s.value for s in Stat.objects.all()}

    return render(request, "dashboard/index.html", {"stats": stats})
