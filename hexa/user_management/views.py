from django.shortcuts import render


def account(request):
    return render(request, "user_management/account.html", {"user": request.user})
