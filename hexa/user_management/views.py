from django.contrib.auth import logout as do_logout
from django.shortcuts import render, redirect


def account(request):
    return render(request, "user_management/account.html", {"user": request.user})


def logout(request):
    do_logout(request)

    return redirect("login")
