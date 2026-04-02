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

from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.webapps.utils import extract_webapp_subdomain
from hexa.webapps.views import serve_webapp

WEBAPP_SESSION_COOKIE = "hexa_webapp_session"
WEBAPP_SESSION_MAX_AGE = 60 * 60  # 1 hour
AUTH_TOKEN_MAX_AGE = 30


def _webapp_not_found():
    html = render_to_string("webapps/404.html")
    return HttpResponse(html, status=404)


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


# FIXME: This is okay for now, but there's no reason why we can't serve these
# on subdomains as well in the future.
def _serve_iframe_or_superset_webapp(webapp):
    return HttpResponseRedirect(webapp.url)


def _build_auth_token_url(request, webapp):
    query = request.GET.copy()
    query.pop("auth_token", None)
    clean_path = request.path
    if query:
        clean_path = f"{clean_path}?{query.urlencode()}"
    current_url = request.build_absolute_uri(clean_path)
    return f"{settings.BASE_URL}/webapps/{webapp.pk}/auth-token/?{urlencode({'next': current_url})}"


def _set_webapp_session_cookie(response, session_key, request_host):
    response.set_cookie(
        WEBAPP_SESSION_COOKIE,
        session_key,
        max_age=WEBAPP_SESSION_MAX_AGE,
        httponly=True,
        secure=getattr(settings, "SESSION_COOKIE_SECURE", False),
        # Lax so the cookie is sent on the cross-domain redirect from the main app
        samesite="Lax",
        domain=request_host,
    )


def _handle_auth_token(request, webapp):
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

    session = SessionStore()
    session.set_expiry(WEBAPP_SESSION_MAX_AGE)
    session["user_id"] = str(user.pk)
    session["webapp_id"] = str(webapp.pk)
    session.create()

    # Redirect to the same URL without the auth_token parameter
    query = request.GET.copy()
    query.pop("auth_token")
    clean_path = request.path
    if query:
        clean_path = f"{clean_path}?{query.urlencode()}"
    redirect_url = request.build_absolute_uri(clean_path)

    response = HttpResponseRedirect(redirect_url)
    _set_webapp_session_cookie(
        response, session.session_key, request.get_host().split(":")[0]
    )
    return response


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

        if not webapp.is_public:
            if request.GET.get("auth_token"):
                return _handle_auth_token(request, webapp)

            user = _check_webapp_session(request, webapp)
            if not user:
                return HttpResponseRedirect(_build_auth_token_url(request, webapp))

        if webapp.type == Webapp.WebappType.STATIC:
            response = _serve_static_webapp(webapp, request)
        else:
            response = _serve_iframe_or_superset_webapp(webapp)

        return response

    return middleware
