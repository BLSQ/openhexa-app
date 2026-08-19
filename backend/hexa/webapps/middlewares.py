import json
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseNotModified,
    HttpResponseRedirect,
    JsonResponse,
)
from django.template.loader import render_to_string
from django.utils import timezone

from hexa.superset.views import view_superset_dashboard
from hexa.user_management.models import User
from hexa.webapps.graphql_proxy import handle_graphql_proxy
from hexa.webapps.models import GitWebapp, SupersetWebapp, Webapp, WebappUser
from hexa.webapps.utils import (
    PREVIEW_KEY_RE,
    extract_webapp_subdomain,
    powered_by_url,
    webapp_host_url,
)
from hexa.webapps.views import serve_webapp

WEBAPP_SESSION_COOKIE = "hexa_webapp_session"
WEBAPP_SESSION_MAX_AGE = 4 * 60 * 60  # 4 hours
AUTH_TOKEN_MAX_AGE = 30

SESSION_USER_ID = "user_id"
SESSION_WEBAPP_ID = "webapp_id"
PREVIEW_KEYS_FIELD = "webapp_preview_keys"

POWERED_BY_BANNER_HEIGHT = "2.25rem"


def _webapp_not_found():
    html = render_to_string("webapps/404.html")
    return HttpResponse(html, status=404)


def _set_csp_frame_ancestors(response):
    frame_ancestors = f"'self' {settings.BASE_URL}"
    if hasattr(settings, "NEW_FRONTEND_DOMAIN"):
        frame_ancestors += f" {settings.NEW_FRONTEND_DOMAIN}"
    del response["X-Frame-Options"]
    response["Content-Security-Policy"] = f"frame-ancestors {frame_ancestors}"
    response["Referrer-Policy"] = "no-referrer"


def _serve_static_webapp(webapp, request):
    try:
        git_webapp = GitWebapp.objects.get(pk=webapp.pk)
    except GitWebapp.DoesNotExist:
        return _webapp_not_found()

    # Cache strategy: tie the ETag to the published commit so a new publish
    # immediately invalidates clients (no time-based staleness window), and
    # pair it with `no-cache` so browsers revalidate on every request instead
    # of trusting their local copy. The 304 short-circuit avoids the Forgejo
    # round-trip when the content hasn't changed.
    etag = f'W/"{git_webapp.published_commit}"' if git_webapp.published_commit else None
    if etag and request.META.get("HTTP_IF_NONE_MATCH") == etag:
        return HttpResponseNotModified()

    path = request.path.lstrip("/") or "index.html"
    response = serve_webapp(request, git_webapp, path)
    if etag:
        cache_scope = "public" if webapp.is_public else "private"
        response["Cache-Control"] = f"{cache_scope}, no-cache"
        response["ETag"] = etag
    return response


def _serve_iframe_webapp(webapp, show_powered_by=False, powered_by_url=None):
    html = render_to_string(
        "webapps/embed.html",
        {
            "name": webapp.name,
            "url": webapp.url,
            "show_powered_by": show_powered_by,
            "powered_by_url": powered_by_url,
        },
    )
    return HttpResponse(html)


def _inject_powered_by_banner(response, powered_by_url):
    content_type = response.get("Content-Type", "")
    if "text/html" not in content_type:
        return response

    # The partial renders a spacer plus the fixed banner so the webapp content is
    # pushed up rather than covered (HEXA-1751); banner_height keeps both in sync.
    banner_html = render_to_string(
        "webapps/_powered_by_banner.html",
        {
            "powered_by_url": powered_by_url,
            "banner_height": POWERED_BY_BANNER_HEIGHT,
        },
    )
    content = response.content.decode(response.charset)
    closing_body = content.rfind("</body>")
    if closing_body == -1:
        content += banner_html
    else:
        content = content[:closing_body] + banner_html + content[closing_body:]
    response.content = content.encode(response.charset)
    response["Content-Length"] = len(response.content)
    return response


def _inject_openhexa_context(response, webapp):
    """Inject `window.OPENHEXA = {...}` into HTML responses so webapp JS knows its workspace."""
    content_type = response.get("Content-Type", "")
    if "text/html" not in content_type:
        return response

    context = {
        "workspaceSlug": webapp.workspace.slug,
        "webappSlug": webapp.slug,
        "isPublic": webapp.is_public,
    }
    snippet = f"<script>window.OPENHEXA=Object.freeze({json.dumps(context)});</script>"

    content = response.content.decode(response.charset)
    head_close = content.find("</head>")
    if head_close == -1:
        # No <head> — likely a fragment or non-page asset served as text/html. Skip injection.
        return response
    content = content[:head_close] + snippet + content[head_close:]
    response.content = content.encode(response.charset)
    response["Content-Length"] = len(response.content)
    return response


def _dispatch_webapp_response(request, webapp, show_powered_by=False):
    if webapp.type == Webapp.WebappType.STATIC:
        response = _serve_static_webapp(webapp, request)
        response = _inject_openhexa_context(response, webapp)
        if show_powered_by:
            response = _inject_powered_by_banner(
                response, powered_by_url(request, "static")
            )
    elif webapp.type == Webapp.WebappType.SUPERSET:
        response = _serve_superset_webapp(request, webapp)
    else:
        response = _serve_iframe_webapp(
            webapp,
            show_powered_by=show_powered_by,
            powered_by_url=powered_by_url(request, "iframe")
            if show_powered_by
            else None,
        )
    return response


def _serve_superset_webapp(request, webapp):
    superset_webapp = SupersetWebapp.objects.select_related("superset_dashboard").get(
        pk=webapp.pk
    )
    return view_superset_dashboard(request, superset_webapp.superset_dashboard.id)


def _build_auth_token_url(request, webapp):
    query = request.GET.copy()
    query.pop("auth_token", None)
    clean_path = request.path
    if query:
        clean_path = f"{clean_path}?{query.urlencode()}"
    current_url = request.build_absolute_uri(clean_path)
    return f"{settings.BASE_URL}/webapps/{webapp.pk}/auth-token/?{urlencode({'next': current_url})}"


def _validate_auth_token(request, webapp):
    """Validate the auth_token and return the authenticated user, or an error response."""
    token = request.GET.get("auth_token")
    signer = TimestampSigner()
    try:
        payload = signer.unsign_object(token, max_age=AUTH_TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return HttpResponseRedirect(_build_auth_token_url(request, webapp))

    if payload.get("subdomain") != webapp.subdomain:
        return HttpResponse("Forbidden", status=403)

    try:
        user = User.objects.get(pk=payload["user_id"])
    except User.DoesNotExist:
        return HttpResponseRedirect(_build_auth_token_url(request, webapp))

    if not Webapp.objects.filter_for_user(user).filter(pk=webapp.pk).exists():
        return HttpResponse("Forbidden", status=403)

    return user


def _create_webapp_session(webapp, user):
    session = SessionStore()
    session.set_expiry(WEBAPP_SESSION_MAX_AGE)
    session[SESSION_USER_ID] = str(user.pk)
    session[SESSION_WEBAPP_ID] = str(webapp.pk)
    session.create()
    return session


def _preview_session_is_valid(session_key, webapp, user):
    if not Session.objects.filter(
        session_key=session_key, expire_date__gt=timezone.now()
    ).exists():
        return False
    store = SessionStore(session_key=session_key)
    return store.get(SESSION_WEBAPP_ID) == str(webapp.pk) and store.get(
        SESSION_USER_ID
    ) == str(user.pk)


def get_or_create_preview_session_key(request, webapp, user):
    """Return a webapp preview session key for (user, webapp), reusing the
    current one until it expires.
    """
    keys = request.session.get(PREVIEW_KEYS_FIELD, {})
    existing = keys.get(str(webapp.pk))
    if existing and _preview_session_is_valid(existing, webapp, user):
        return existing

    session = _create_webapp_session(webapp, user)
    request.session[PREVIEW_KEYS_FIELD] = {
        **keys,
        str(webapp.pk): session.session_key,
    }
    return session.session_key


def get_or_create_preview_url(request, webapp, user):
    """Preview URL for (user, webapp): the (rotating) session key as the first
    DNS label of the webapp host, so it authenticates without a cookie.
    """
    return webapp_host_url(get_or_create_preview_session_key(request, webapp, user))


def _check_webapp_session(request, webapp):
    session_key = request.COOKIES.get(WEBAPP_SESSION_COOKIE)
    if not session_key:
        return None

    session = SessionStore(session_key=session_key)
    stored_user_id = session.get(SESSION_USER_ID)
    stored_webapp_id = session.get(SESSION_WEBAPP_ID)
    if stored_webapp_id != str(webapp.pk) or not stored_user_id:
        return None

    try:
        user = User.objects.get(pk=stored_user_id)
    except User.DoesNotExist:
        return None

    request.user = WebappUser.from_user(user, webapp)
    return request.user


def _webapp_from_session_key(session_key):
    """Return the webapp referenced by a preview session whose key matches the
    given DNS label, or None. The session key travels in the hostname so the
    iframe can authenticate without a third-party cookie.
    """
    if not PREVIEW_KEY_RE.match(session_key):
        return None
    webapp_id = SessionStore(session_key=session_key).get(SESSION_WEBAPP_ID)
    if not webapp_id:
        return None
    try:
        return Webapp.objects.get(pk=webapp_id)
    except Webapp.DoesNotExist:
        return None


def _handle_webapp_request(request, webapp, *, request_has_user=True):
    """Shared auth + serve logic for both webapp middlewares."""
    if request.path.startswith("/graphql/"):
        if webapp.is_public:
            return HttpResponseNotFound("Not available")

        if not _check_webapp_session(request, webapp):
            return JsonResponse(
                {"errors": [{"message": "Authentication required"}]},
                status=401,
            )

        return handle_graphql_proxy(request, webapp)

    has_valid_token = False
    if request.GET.get("auth_token"):
        result = _validate_auth_token(request, webapp)
        if isinstance(result, HttpResponse):
            if not webapp.is_public:
                return result
        else:
            has_valid_token = True
            if not webapp.is_public:
                session = _create_webapp_session(webapp, result)

                query = request.GET.copy()
                query.pop("auth_token")
                clean_path = request.path
                if query:
                    clean_path = f"{clean_path}?{query.urlencode()}"
                redirect_response = HttpResponseRedirect(clean_path)
                redirect_response.set_cookie(
                    WEBAPP_SESSION_COOKIE,
                    session.session_key,
                    max_age=WEBAPP_SESSION_MAX_AGE,
                    httponly=True,
                    secure=True,
                    samesite="None",
                )
                return redirect_response

    if not webapp.is_public:
        if not _check_webapp_session(request, webapp):
            return HttpResponseRedirect(_build_auth_token_url(request, webapp))

    is_authenticated = (
        (request_has_user and request.user.is_authenticated)
        or has_valid_token
        or bool(_check_webapp_session(request, webapp))
    )
    show_powered_by = (
        webapp.is_public and webapp.show_powered_by and not is_authenticated
    )

    response = _dispatch_webapp_response(request, webapp, show_powered_by)
    _set_csp_frame_ancestors(response)
    return response


def webapp_subdomain_middleware(get_response):
    """Intercepts requests to webapp subdomains (e.g. my-app.webapps.openhexa.org)
    and serves the webapp content directly, bypassing the normal Django URL routing.

    Requests that don't match a webapp subdomain are passed through unchanged.

    For private webapps, authentication works via cross-subdomain token exchange:

    1. Visitor hits my-app.webapps.openhexa.org
    2. Middleware redirects to main app: openhexa.org/webapps/<id>/auth-token/?next=<url>
    3. Main app's `login_required_middleware` ensures the user is logged in
    4. `auth_token` view signs a short-lived token (30s) with the `user_id` and `subdomain`
    5. User is redirected back to the webapp subdomain with ?auth_token=<token>
    6. Middleware validates the token, creates a DB-backed session scoped to the subdomain,
       sets a `hexa_webapp_session` cookie, and redirects to strip the token from the URL
    7. Subsequent requests use the session cookie (no more redirects). The cookie
       is valid for 1 hour.
    """

    def middleware(request: HttpRequest):
        subdomain = extract_webapp_subdomain(request.get_host())
        if not subdomain:
            return get_response(request)

        webapp = _webapp_from_session_key(subdomain)
        if webapp is not None:
            request.COOKIES[WEBAPP_SESSION_COOKIE] = subdomain
        else:
            try:
                webapp = Webapp.objects.get(subdomain=subdomain)
            except Webapp.DoesNotExist:
                return _webapp_not_found()

        request.webapp = webapp
        return _handle_webapp_request(request, webapp, request_has_user=True)

    return middleware


def custom_domain_middleware(get_response):
    """Intercepts requests arriving on a webapp's custom domain and serves the webapp
    content directly bypassing normal Django URL routing.
    """

    def middleware(request: HttpRequest):
        host = request.META.get("HTTP_HOST", "").split(":")[0].lower()

        # Skip the DB query for known OpenHEXA hosts — only custom domains are unusual
        webapps_domain = getattr(settings, "WEBAPPS_DOMAIN", None)
        if host == settings.BASE_HOSTNAME or (
            webapps_domain and host.endswith(f".{webapps_domain}")
        ):
            return get_response(request)

        try:
            webapp = Webapp.objects.get(custom_domain=host)
        except Webapp.DoesNotExist:
            return get_response(request)

        request.webapp = webapp
        return _handle_webapp_request(request, webapp, request_has_user=False)

    return middleware
