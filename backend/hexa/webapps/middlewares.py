from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)

from hexa.webapps.models import GitWebapp, Webapp
from hexa.webapps.views import serve_webapp


def _serve_static_webapp(webapp, request):
    try:
        git_webapp = GitWebapp.objects.get(pk=webapp.pk)
    except GitWebapp.DoesNotExist:
        return HttpResponseNotFound("Webapp not found")

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


def webapp_subdomain_middleware(get_response):
    def middleware(request: HttpRequest):
        # Check if subdomain for webapps is enabled, skip middleware if not
        subdomain_base_url = getattr(settings, "WEBAPPS_SUBDOMAIN_BASE_URL", None)
        if not subdomain_base_url:
            return get_response(request)

        # Remove port if any (for example for local testing)
        subdomain_base = subdomain_base_url.split(":")[0]
        request_host = request.get_host().split(":")[0]

        # Check if we're calling a valid webapps subdomain
        if not request_host.endswith(f".{subdomain_base}"):
            return get_response(request)

        subdomain = request_host.replace(f".{subdomain_base}", "")
        if not subdomain or "." in subdomain:
            return get_response(request)

        try:
            webapp = Webapp.objects.get(subdomain=subdomain)
        except Webapp.DoesNotExist:
            return HttpResponseNotFound("Webapp not found")

        if not webapp.is_public:
            # TODO: check if short-lived token is present, if not redirect to
            # web apps auth endpoint on main OH app
            pass

        if webapp.type == Webapp.WebappType.STATIC:
            response = _serve_static_webapp(webapp, request)
        else:
            response = _serve_iframe_or_superset_webapp(webapp)

        return response

    return middleware
