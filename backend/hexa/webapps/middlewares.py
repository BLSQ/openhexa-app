from urllib.parse import urlencode

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.template.loader import render_to_string

from hexa.superset.views import view_superset_dashboard
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, SupersetWebapp, Webapp
from hexa.webapps.utils import extract_webapp_subdomain
from hexa.webapps.views import serve_webapp

WEBAPP_SESSION_COOKIE = "hexa_webapp_session"
WEBAPP_SESSION_MAX_AGE = 60 * 60  # 1 hour
AUTH_TOKEN_MAX_AGE = 30

POWERED_BY_BANNER_HTML = """<div style="position:fixed;bottom:0;left:0;right:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;border-top:1px solid #e5e7eb;background-color:#f9fafb;padding:0.5rem 0;font-family:Inter,system-ui,-apple-system,sans-serif;font-size:0.75rem;color:#6b7280">Powered by <a href="https://www.openhexa.com" target="_blank" rel="noopener noreferrer" style="margin-left:0.25rem;display:flex;align-items:center;gap:0.25rem;font-weight:500;color:#2563eb;text-decoration:none"><img alt="OpenHEXA" style="height:1rem;width:1rem" src="data:image/svg+xml,%3Csvg width='165' height='188' viewBox='0 0 165 188' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cg clip-path='url(%23clip0)'%3E%3Cpath fill-rule='evenodd' clip-rule='evenodd' d='M165.21 56.7599C165.21 50.5199 160.81 42.8299 155.44 39.6699L92.6901 2.7699C87.3101 -0.390097 78.5201 -0.390097 73.1401 2.7699L10.4001 39.6699C5.03013 42.8399 0.630127 50.5199 0.630127 56.7599V130.88C0.630127 137.12 5.03013 144.81 10.4001 147.97L73.1401 184.87C78.5201 188.03 87.3101 188.03 92.6901 184.87L155.43 147.97C160.81 144.81 165.2 137.12 165.2 130.88V56.7599H165.21Z' fill='%23FF3E96'/%3E%3Cpath fill-rule='evenodd' clip-rule='evenodd' d='M165.21 56.7599C165.21 50.5199 160.81 42.8299 155.44 39.6699L92.6901 2.7699C87.3101 -0.390097 78.5201 -0.390097 73.1401 2.7699L10.4001 39.6699C5.03013 42.8399 0.630127 50.5199 0.630127 56.7599V130.88C0.630127 137.12 5.03013 144.81 10.4001 147.97L73.1401 184.87C78.5201 188.03 87.3101 188.03 92.6901 184.87L155.43 147.97C160.81 144.81 165.2 137.12 165.2 130.88V56.7599H165.21Z' fill='url(%23paint0_linear)'/%3E%3Cpath d='M77.4002 156.51C75.8302 156.51 74.2302 156.1 72.7902 155.23L29.7902 129.5C27.0702 127.88 25.4102 124.94 25.4102 121.78V64.87C25.4102 61.62 27.1602 58.63 29.9902 57.03L59.5802 40.34C62.3702 38.77 65.7802 38.79 68.5402 40.41C71.3002 42.02 73.0002 44.98 73.0002 48.18V76.97L106.36 96.48C109.12 98.09 110.82 101.05 110.82 104.25V124.07L122.41 117.53V70.97L83.8102 47.86C79.5502 45.31 78.1602 39.78 80.7102 35.52C83.2602 31.26 88.7902 29.87 93.0502 32.42L136.04 58.15C138.76 59.77 140.42 62.71 140.42 65.87V122.78C140.42 126.03 138.67 129.02 135.84 130.62L106.25 147.31C103.46 148.88 100.05 148.86 97.2902 147.24C94.5302 145.63 92.8302 142.67 92.8302 139.47V109.4L59.4702 89.9C56.7102 88.29 55.0102 85.33 55.0102 82.13V63.58L43.4202 70.12V116.67L82.0402 139.78C86.3002 142.33 87.6902 147.86 85.1402 152.12C83.4502 154.95 80.4602 156.51 77.4002 156.51Z' fill='white'/%3E%3C/g%3E%3Cdefs%3E%3ClinearGradient id='paint0_linear' x1='124.789' y1='21.3012' x2='41.05' y2='166.341' gradientUnits='userSpaceOnUse'%3E%3Cstop offset='1.86995e-07' stop-color='white' stop-opacity='0.4'/%3E%3Cstop offset='1' stop-color='white' stop-opacity='0'/%3E%3C/linearGradient%3E%3CclipPath id='clip0'%3E%3Crect width='165' height='188' fill='white'/%3E%3C/clipPath%3E%3C/defs%3E%3C/svg%3E">OpenHEXA</a></div>"""


def _webapp_not_found():
    html = render_to_string("webapps/404.html")
    return HttpResponse(html, status=404)


def _set_csp_frame_ancestors(response):
    frame_ancestors = f"'self' {settings.BASE_URL}"
    if hasattr(settings, "NEW_FRONTEND_DOMAIN"):
        frame_ancestors += f" {settings.NEW_FRONTEND_DOMAIN}"
    del response["X-Frame-Options"]
    response["Content-Security-Policy"] = f"frame-ancestors {frame_ancestors}"


def _serve_static_webapp(webapp, request):
    try:
        git_webapp = GitWebapp.objects.get(pk=webapp.pk)
    except GitWebapp.DoesNotExist:
        return _webapp_not_found()

    path = request.path.lstrip("/") or "index.html"
    response = serve_webapp(request, git_webapp, path)
    if git_webapp.published_commit:
        cache_scope = "public" if webapp.is_public else "private"
        response["Cache-Control"] = f"{cache_scope}, max-age=300"
    return response


def _serve_iframe_webapp(webapp, show_powered_by=False):
    html = render_to_string(
        "webapps/embed.html",
        {"name": webapp.name, "url": webapp.url, "show_powered_by": show_powered_by},
    )
    return HttpResponse(html)


def _inject_powered_by_banner(response):
    content_type = response.get("Content-Type", "")
    if "text/html" not in content_type:
        return response

    content = response.content.decode(response.charset)
    closing_body = content.rfind("</body>")
    if closing_body == -1:
        content += POWERED_BY_BANNER_HTML
    else:
        content = (
            content[:closing_body] + POWERED_BY_BANNER_HTML + content[closing_body:]
        )
    response.content = content.encode(response.charset)
    response["Content-Length"] = len(response.content)
    return response


def _dispatch_webapp_response(request, webapp, show_powered_by=False):
    if webapp.type == Webapp.WebappType.STATIC:
        response = _serve_static_webapp(webapp, request)
        if show_powered_by:
            _inject_powered_by_banner(response)
    elif webapp.type == Webapp.WebappType.SUPERSET:
        response = _serve_superset_webapp(request, webapp)
    else:
        response = _serve_iframe_webapp(webapp, show_powered_by=show_powered_by)
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
    session["user_id"] = str(user.pk)
    session["webapp_id"] = str(webapp.pk)
    session.create()
    return session


def _check_webapp_session(request, webapp):
    session_key = request.COOKIES.get(WEBAPP_SESSION_COOKIE)
    if not session_key:
        return None

    session = SessionStore(session_key=session_key)
    stored_user_id = session.get("user_id")
    stored_webapp_id = session.get("webapp_id")
    if stored_webapp_id != str(webapp.pk) or not stored_user_id:
        return None

    try:
        user = User.objects.get(pk=stored_user_id)
    except User.DoesNotExist:
        return None

    request.user = user
    return user


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

        try:
            webapp = Webapp.objects.get(subdomain=subdomain)
        except Webapp.DoesNotExist:
            return _webapp_not_found()

        request.webapp = webapp

        # TODO: Explicitly block this for now, but in v2 we'll probably re-route
        # here to the main app based on the webapps permission scopes to access
        # workspace resources.
        if request.path.startswith("/graphql/"):
            return HttpResponseNotFound("Not available")

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
            request.user.is_authenticated
            or has_valid_token
            or _check_webapp_session(request, webapp)
        )
        show_powered_by = (
            webapp.is_public and webapp.show_powered_by and not is_authenticated
        )

        response = _dispatch_webapp_response(request, webapp, show_powered_by)
        _set_csp_frame_ancestors(response)

        return response

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

        if request.path.startswith("/graphql/"):
            return HttpResponseNotFound("Not available")

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
            request.user.is_authenticated
            or has_valid_token
            or _check_webapp_session(request, webapp)
        )
        show_powered_by = (
            webapp.is_public and webapp.show_powered_by and not is_authenticated
        )

        response = _dispatch_webapp_response(request, webapp, show_powered_by)
        _set_csp_frame_ancestors(response)

        return response

    return middleware
