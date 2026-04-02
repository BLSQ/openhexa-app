import mimetypes
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.core.signing import TimestampSigner
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_GET

from hexa.files.utils import is_safe_path
from hexa.git.forgejo import ForgejoAPIError, get_forgejo_client
from hexa.webapps.models import GitWebapp, Webapp
from hexa.webapps.utils import extract_webapp_subdomain


@require_GET
def auth_token(request, webapp_id):
    """
    Endpoint that's used to verify if a user has access to a private web app.
    If the user is authenticated and has access to the webapp, then create a
    timestamp signed token and redirect back to the webapp (with the token
    in the query params).
    """
    webapp = get_object_or_404(Webapp, pk=webapp_id)

    next_url = request.GET.get("next", "")
    if not next_url:
        return HttpResponseBadRequest("Missing next parameter")

    parsed_next_url = urlparse(next_url)
    if extract_webapp_subdomain(parsed_next_url.hostname or "") != webapp.subdomain:
        return HttpResponseBadRequest("Invalid redirect target")

    user = request.user
    should_have_access = (
        webapp.is_public
        or Webapp.objects.filter_for_user(user).filter(pk=webapp.pk).exists()
    )

    if not should_have_access:
        return HttpResponse("Forbidden", status=403)

    signer = TimestampSigner()
    token = signer.sign_object({"user_id": str(user.id), "subdomain": webapp.subdomain})

    query_params = parse_qs(parsed_next_url.query)
    query_params["auth_token"] = [token]
    redirect_url = urlunparse(
        parsed_next_url._replace(query=urlencode(query_params, doseq=True))
    )
    return HttpResponseRedirect(redirect_url)


def _check_access(request, webapp: Webapp):
    if webapp.is_public:
        return None
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"/login?next={request.path}")
    if not Webapp.objects.filter_for_user(request.user).filter(pk=webapp.pk).exists():
        return HttpResponse("Forbidden", status=403)
    return None


# TODO: refactor to allow both subdomain + path serving?
@xframe_options_exempt
def serve_webapp(request, webapp_id, path="index.html"):
    try:
        git_webapp = GitWebapp.objects.select_related("workspace").get(pk=webapp_id)
    except GitWebapp.DoesNotExist:
        return HttpResponseNotFound("Webapp not found")

    denied = _check_access(request, git_webapp)
    if denied:
        return denied

    if not is_safe_path(path):
        return HttpResponseBadRequest("Invalid path")

    if not git_webapp.published_commit:
        return HttpResponseNotFound("No published version")

    client = get_forgejo_client()

    try:
        content = client.get_file(
            git_webapp.repository,
            path,
            git_webapp.published_commit,
            org_slug=git_webapp.git_org.slug,
        )
    except ForgejoAPIError as e:
        if e.status_code == 404:
            if path == "index.html":
                return HttpResponseNotFound("No index.html found")
            return HttpResponseNotFound("File not found")
        raise

    content_type, _ = mimetypes.guess_type(path)
    if not content_type:
        content_type = "application/octet-stream"

    return HttpResponse(content, content_type=content_type)
