import mimetypes
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
    if webapp.is_public:
        return True

    if not request.user.is_authenticated:
        return False

    return webapp.workspace.members.filter(id=request.user.id).exists()


def _resolve_bundle_file_path(webapp: Webapp, requested_path: str) -> str | None:
    """
    Resolve requested path to actual file path in bundle manifest.
    Handles common prefixes like build/ and dist/.
    """
    manifest = webapp.bundle_manifest or []
    available_files = [f["path"] for f in manifest]

    if requested_path in available_files:
        return requested_path

    for file_path in available_files:
        if file_path.endswith(requested_path):
            return file_path

    for prefix in ["build/", "dist/", ""]:
        candidate = prefix + requested_path
        if candidate in available_files:
            return candidate

    return None


@xframe_options_sameorigin
def serve_webapp_html(
    request: HttpRequest, workspace_slug: str, webapp_slug: str
) -> HttpResponse:
    """Serve content for HTML type webapps."""
    workspace = get_object_or_404(Workspace, slug=workspace_slug, archived=False)
    webapp = get_object_or_404(Webapp, workspace=workspace, slug=webapp_slug)

    if not _check_webapp_permission(request, webapp):
        raise Http404("Webapp not found")

    if webapp.type != Webapp.WebappType.HTML:
        raise Http404("Not an HTML webapp")

    if not webapp.content:
        return HttpResponse("No content available", status=404)

    return HttpResponse(webapp.content, content_type="text/html; charset=utf-8")


def _read_file_from_storage(storage, bucket_name: str, object_key: str) -> bytes:
    """Read file content from storage backend."""
    if hasattr(storage, "path"):
        file_path = str(storage.path(bucket_name, object_key))
        with open(file_path, "rb") as f:
            return f.read()
    else:
        from google.cloud import storage as gcp_storage

        client = gcp_storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_key)
        return blob.download_as_bytes()


@xframe_options_sameorigin
def serve_webapp_bundle(
    request: HttpRequest, workspace_slug: str, webapp_slug: str, path: str = ""
) -> HttpResponse:
    """Serve files from Bundle type webapps."""
    from hexa.files import storage

    workspace = get_object_or_404(Workspace, slug=workspace_slug, archived=False)
    webapp = get_object_or_404(Webapp, workspace=workspace, slug=webapp_slug)

    if not _check_webapp_permission(request, webapp):
        raise Http404("Webapp not found")

    if webapp.type != Webapp.WebappType.BUNDLE:
        raise Http404("Not a Bundle webapp")

    if not webapp.bundle_manifest:
        return HttpResponse("No bundle available", status=404)

    if not path:
        path = "index.html"

    requested_path = Path(path)
    if (
        requested_path.is_absolute()
        or ".." in requested_path.parts
        or any(part.startswith(".") for part in requested_path.parts)
    ):
        raise Http404("Invalid path")

    storage_path = _resolve_bundle_file_path(webapp, path)
    if not storage_path:
        raise Http404(f"File not found in bundle: {path}")

    bucket_name = workspace.bucket_name
    object_key = f"webapps/{webapp.slug}/{storage_path}"

    try:
        storage.get_bucket_object(bucket_name, object_key)

        content_type, _ = mimetypes.guess_type(path)
        if not content_type:
            content_type = "application/octet-stream"

        content = _read_file_from_storage(storage, bucket_name, object_key)

        return HttpResponse(content, content_type=content_type)

    except Exception as e:
        if hasattr(storage, "exceptions") and isinstance(
            e, storage.exceptions.NotFound
        ):
            raise Http404("File not found in storage")
        raise
