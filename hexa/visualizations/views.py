import mimetypes
import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from .models import ExternalDashboard


def dashboard_image(request: HttpRequest, dashboard_id: uuid.UUID) -> HttpResponse:
    dashboard = get_object_or_404(
        ExternalDashboard.objects.filter_for_user(request.user),
        pk=dashboard_id,
    )

    if dashboard.picture == "__OVERRIDE_TEST__":
        # special key to enable this call without doing a filesystem check -- useful in test case
        return HttpResponse("")

    return HttpResponse(
        dashboard.picture.file.read(),
        content_type=mimetypes.guess_type(dashboard.picture.name)[0],
    )
