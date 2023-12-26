from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


@require_POST
def accept_tos(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and not request.user.accepted_tos:
        request.user.accepted_tos = True
        request.user.save()

    return redirect(reverse("core:login"))
