import mimetypes
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse

from django.conf import settings
from django.core.signing import TimestampSigner
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_http_methods

from hexa.files.utils import is_safe_path
from hexa.git.exceptions import GitFileNotFound
from hexa.git.forgejo import get_forgejo_client
from hexa.user_management.utils import has_configured_two_factor
from hexa.webapps.models import Webapp
from hexa.webapps.utils import extract_webapp_subdomain, is_local_dev_origin


def _needs_login(user):
    return not user.is_authenticated or (
        has_configured_two_factor(user) and not user.is_verified()
    )


def _login_redirect(request):
    """Send the visitor to the frontend login, returning to this exact URL after.

    `next` has to be absolute: the login page lives on the frontend domain and
    resolves a relative `next` against its own origin. On deployments where the
    backend answers on a host of its own (api.<env> vs app.<env>), a relative
    `next` would send the user back to a frontend URL that doesn't exist.
    """
    current_absolute_url = request.build_absolute_uri(request.get_full_path())
    return HttpResponseRedirect(
        f"{settings.NEW_FRONTEND_DOMAIN}/login?next={quote(current_absolute_url)}"
    )


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
    parsed_hostname = parsed_next_url.hostname or ""
    subdomain_match = extract_webapp_subdomain(parsed_hostname) == webapp.subdomain
    custom_domain_match = (
        bool(webapp.custom_domain) and parsed_hostname == webapp.custom_domain
    )
    if not subdomain_match and not custom_domain_match:
        return HttpResponseBadRequest("Invalid redirect target")

    if not request.user.is_authenticated:
        return _login_redirect(request)

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


def serve_webapp(request, git_webapp, path="index.html"):
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
    except GitFileNotFound:
        if path == "index.html":
            return HttpResponseNotFound("No index.html found")
        return HttpResponseNotFound("File not found")

    content_type, _ = mimetypes.guess_type(path)
    if not content_type:
        content_type = "application/octet-stream"

    return HttpResponse(content, content_type=content_type)


@require_GET
def dev_js(request):
    """Serve the local-development shim.

    Authors include this script from their local page; it sets `window.OPENHEXA`
    and reroutes `/graphql/` calls to the webapp's rotating preview URL (obtained
    through the authenticated `dev_auth` handshake). Must stay anonymous so a
    cross-origin `<script src>` isn't redirected to login.
    """
    js = render_to_string("webapps/dev.js", {"base_url": settings.BASE_URL})
    return HttpResponse(js, content_type="application/javascript")


def _resolve_dev_webapp(workspace_slug, webapp_slug):
    if not (workspace_slug and webapp_slug):
        return None
    return Webapp.objects.filter(
        workspace__slug=workspace_slug, slug=webapp_slug
    ).first()


def _selectable_dev_webapps(user):
    """Private static webapps the user can develop against (the picker list)."""
    return (
        Webapp.objects.filter_for_user(user)
        .filter(type=Webapp.WebappType.STATIC, is_public=False)
        .select_related("workspace")
        .order_by("workspace__name", "name")
    )


def _set_dev_auth_headers(response):
    response["Content-Security-Policy"] = "frame-ancestors 'none'"
    response["X-Frame-Options"] = "DENY"
    response["Cross-Origin-Opener-Policy"] = "unsafe-none"
    return response


def _render_authorize(request, webapps, origin, selected=None):
    """Render the authorization screen: a selectable list of web apps and a single
    Approve button. Picker and preselected modes are the same UI — when a web app
    is provided it is preselected; otherwise the user selects one before approving.
    """
    return _set_dev_auth_headers(
        render(
            request,
            "webapps/dev_auth_authorize.html",
            {
                "webapps": webapps,
                "origin": origin,
                "selected_ws": selected.workspace.slug if selected else "",
                "selected_app": selected.slug if selected else "",
            },
        )
    )


@require_http_methods(["GET", "POST"])
def dev_auth(request):
    """Authenticated handshake that hands a rotating preview URL to a local page."""
    params = request.POST if request.method == "POST" else request.GET
    origin = params.get("origin", "")
    # The origin becomes the postMessage target for the credential, so only
    # accept local-dev origins: an opaque file:// page (null/file://) or a
    # concrete localhost URL. Anything remote (e.g. https://evil.com) is rejected.
    is_opaque = origin in {"null", "file://"}
    if not is_opaque and not is_local_dev_origin(origin):
        return HttpResponseBadRequest("Invalid origin")

    # This view handles its own login bounce (it is in ANONYMOUS_URLS) because the
    # generic one sends a relative `next`, which strands the popup on the frontend.
    if _needs_login(request.user):
        if request.method == "POST":
            return HttpResponse("Authentication required", status=401)
        return _login_redirect(request)

    workspace_slug = params.get("workspaceSlug", "")
    webapp_slug = params.get("webappSlug", "")

    # No webapp specified: let the (authenticated) user pick and approve one from
    # the list. Selecting an app POSTs back with the workspace + webapp.
    if not (workspace_slug and webapp_slug):
        return _render_authorize(request, _selectable_dev_webapps(request.user), origin)

    webapp = _resolve_dev_webapp(workspace_slug, webapp_slug)
    if webapp is None:
        return HttpResponseNotFound("Web app not found")
    if not Webapp.objects.filter_for_user(request.user).filter(pk=webapp.pk).exists():
        return HttpResponse("Forbidden", status=403)

    # The credential is only ever minted on the CSRF-protected POST from the
    # approval screen. A GET must never hand it out: any page served on
    # localhost could otherwise obtain a webapp-scoped credential just by
    # opening this URL with pinned slugs. The preselected app is shown on the
    # same authorization screen as the picker, as a single-item list.
    if request.method == "GET":
        return _render_authorize(request, [webapp], origin, selected=webapp)

    # Deferred import: middlewares imports serve_webapp from this module.
    from hexa.webapps.middlewares import get_or_create_preview_url

    return _set_dev_auth_headers(
        render(
            request,
            "webapps/dev_auth.html",
            {
                "data": {
                    "type": "openhexa-dev-auth",
                    "previewUrl": get_or_create_preview_url(
                        request, webapp, request.user
                    ),
                    "workspaceSlug": webapp.workspace.slug,
                    "webappSlug": webapp.slug,
                },
                "target_origin": "*" if is_opaque else origin,
            },
        )
    )
