import base64
import binascii
from enum import Enum
from urllib.parse import parse_qs, unquote, urlparse

from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET
from oauth2_provider.models import AccessToken

from hexa.webapps.models import GitWebapp

GIT_SCOPE = "openhexa:git"

SERVICE_UPLOAD_PACK = "git-upload-pack"
SERVICE_RECEIVE_PACK = "git-receive-pack"


class Operation(Enum):
    READ = "read"
    WRITE = "write"
    UNSUPPORTED = "unsupported"


def _extract_token(request: HttpRequest) -> str | None:
    """Pull the OAuth2 access token out of the forwarded Authorization header.

    Standard git over HTTP uses Basic auth, where users paste the token as the
    password (the username is irrelevant, commonly "oauth2" or "x-access-token").
    We also accept a Bearer header for clients configured via http.extraHeader.
    """
    header = request.headers.get("Authorization")
    if not header or " " not in header:
        return None

    scheme, _, value = header.partition(" ")
    scheme = scheme.lower()
    value = value.strip()

    if scheme == "bearer":
        return value or None
    if scheme == "basic":
        try:
            decoded = base64.b64decode(value).decode("utf-8")
        except (binascii.Error, ValueError, UnicodeDecodeError):
            return None
        _, _, password = decoded.partition(":")
        return password or None
    return None


def _operation(path: str, query: str) -> Operation:
    """Classify a git smart-HTTP request as a read or a write.

    Pushes use git-receive-pack; reads use git-upload-pack. Everything else
    (Forgejo web UI/API, LFS, archives, dumb-HTTP) is UNSUPPORTED, so the proxy
    only ever forwards clone/fetch/push — those other paths are blocked.
    """
    if path.endswith(SERVICE_RECEIVE_PACK):
        return Operation.WRITE
    if path.endswith(SERVICE_UPLOAD_PACK):
        return Operation.READ
    if path.endswith("info/refs"):
        service = parse_qs(query).get("service", [""])[0]
        if service == SERVICE_RECEIVE_PACK:
            return Operation.WRITE
        if service == SERVICE_UPLOAD_PACK:
            return Operation.READ
    return Operation.UNSUPPORTED


def _parse_target(uri: str) -> tuple[str, str] | None:
    """Extract (org_slug, repository) from a git request URI like
    `/{org}/{repo}.git/info/refs?service=...`.
    """
    parsed = urlparse(uri)
    segments = [s for s in unquote(parsed.path).split("/") if s]
    if len(segments) < 2:
        return None
    org, repo = segments[0], segments[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return org, repo


@require_GET
def authorize(request: HttpRequest) -> HttpResponse:
    """Authorization gate for the git reverse proxy in front of Forgejo.

    nginx issues an auth_request subrequest here for every git operation,
    forwarding the client's Authorization header plus the original URI and
    method. We resolve the token to a user, map the repository to a workspace
    and answer 200 (allow), 401 (no/invalid credentials) or 403 (forbidden).
    nginx only forwards 2xx/401/403 to the client, so all denials map to those.
    """
    token = _extract_token(request)
    if not token:
        return HttpResponse(status=401)

    try:
        access_token = AccessToken.objects.select_related("user").get(token=token)
    except AccessToken.DoesNotExist:
        return HttpResponse(status=401)

    if access_token.is_expired():
        return HttpResponse(status=401)

    if GIT_SCOPE not in access_token.scope.split():
        return HttpResponse(status=403)

    user = access_token.user

    uri = request.headers.get("X-Original-URI")
    if not uri:
        return HttpResponse(status=403)

    target = _parse_target(uri)
    if target is None:
        return HttpResponse(status=403)
    org, repo = target

    parsed = urlparse(uri)
    operation = _operation(unquote(parsed.path), parsed.query)
    if operation is Operation.UNSUPPORTED:
        return HttpResponse(status=403)

    try:
        webapp = (
            GitWebapp.objects.filter_for_user(user)
            .select_related("workspace__organization")
            .get(repository=repo)
        )
    except GitWebapp.DoesNotExist:
        return HttpResponse(status=403)

    if webapp.git_org.slug != org:
        return HttpResponse(status=403)

    if operation is Operation.WRITE and not user.has_perm(
        "webapps.update_webapp", webapp
    ):
        return HttpResponse(status=403)

    return HttpResponse(status=200)
