import io
import mimetypes
import zipfile
from logging import getLogger
from pathlib import Path

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.clickjacking import xframe_options_sameorigin

from hexa.workspaces.models import Workspace

from .models import Webapp

logger = getLogger(__name__)


def _check_webapp_permission(request: HttpRequest, webapp: Webapp) -> bool:
    """Check if user has permission to view the webapp."""
    if not request.user.is_authenticated:
        return False

    return webapp.workspace.members.filter(id=request.user.id).exists()


@xframe_options_sameorigin
def serve_webapp_html(
    request: HttpRequest, workspace_slug: str, webapp_slug: str
) -> HttpResponse:
    """Serve content for HTML type webapps."""
    workspace = get_object_or_404(Workspace, slug=workspace_slug)
    webapp = get_object_or_404(Webapp, workspace=workspace, slug=webapp_slug)

    if not _check_webapp_permission(request, webapp):
        raise Http404("Webapp not found")

    if webapp.type != Webapp.WebappType.HTML:
        raise Http404("Not an HTML webapp")

    if not webapp.content:
        return HttpResponse("No content available", status=404)

    return HttpResponse(webapp.content, content_type="text/html; charset=utf-8")


@xframe_options_sameorigin
def serve_webapp_bundle(
    request: HttpRequest, workspace_slug: str, webapp_slug: str, path: str = ""
) -> HttpResponse:
    """Serve files from Bundle type webapps."""
    workspace = get_object_or_404(Workspace, slug=workspace_slug)
    webapp = get_object_or_404(Webapp, workspace=workspace, slug=webapp_slug)

    if not _check_webapp_permission(request, webapp):
        raise Http404("Webapp not found")

    if webapp.type != Webapp.WebappType.BUNDLE:
        raise Http404("Not a Bundle webapp")

    if not webapp.bundle:
        return HttpResponse("No bundle available", status=404)

    if not path:
        path = "index.html"

    requested_path = Path(path)
    if requested_path.is_absolute() or ".." in requested_path.parts:
        raise Http404("Invalid path")

    try:
        bundle_io = io.BytesIO(webapp.bundle)
        with zipfile.ZipFile(bundle_io, "r") as zip_file:
            available_files = zip_file.namelist()
            file_path = None
            for zip_path in available_files:
                if zip_path.endswith(path) or zip_path == path:
                    file_path = zip_path
                    break

            if not file_path:
                for prefix in ["build/", "dist/", ""]:
                    candidate = prefix + path
                    if candidate in available_files:
                        file_path = candidate
                        break

            if not file_path:
                raise Http404(f"File not found in bundle: {path}")

            file_content = zip_file.read(file_path)
            content_type, _ = mimetypes.guess_type(path)
            if not content_type:
                content_type = "application/octet-stream"

            return HttpResponse(file_content, content_type=content_type)

    except zipfile.BadZipFile:
        logger.error(f"Invalid zip file for webapp {webapp.id}")
        return HttpResponse("Invalid bundle format", status=500)
    except Exception as e:
        logger.error(f"Error serving bundle file: {e}")
        raise Http404("Error reading bundle")
