from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    if request.user.is_authenticated:
        return JsonResponse(
            {"success": True},
            status=200,
        )

    return JsonResponse(
        {"success": False},
        status=401,
    )
