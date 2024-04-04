from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def authenticate(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to authenticate the current user using Django
    session authentication.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {},
            status=401,
        )

    return JsonResponse(
        {"username": request.user.email},
        status=200,
    )
