from django.http import JsonResponse
from django.shortcuts import render


def account(request):
    return render(request, "user_management/account.html", {"user": request.user})


def info(request):
    if request.user.is_authenticated:
        return JsonResponse({"username": request.user.username})

    return JsonResponse({"username": None}, status=401)
