from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def account(request: HttpRequest) -> HttpResponse:
    return render(request, "user_management/account.html", {"user": request.user})
