import mimetypes

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.decorators.clickjacking import xframe_options_exempt

from hexa.git.forgejo import ForgejoAPIError, get_forgejo_client
from hexa.webapps.models import GitWebapp, Webapp


def _check_access(request, webapp: Webapp):
    if webapp.is_public:
        return None
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"/login?next={request.path}")
    if not Webapp.objects.filter_for_user(request.user).filter(pk=webapp.pk).exists():
        return HttpResponse("Forbidden", status=403)
    return None


@xframe_options_exempt
def serve_webapp(request, webapp_id, path="index.html"):
    try:
        webapp = Webapp.objects.select_related("workspace").get(pk=webapp_id)
    except Webapp.DoesNotExist:
        return HttpResponseNotFound("Webapp not found")

    denied = _check_access(request, webapp)
    if denied:
        return denied

    if webapp.type not in (Webapp.WebappType.HTML, Webapp.WebappType.BUNDLE):
        return HttpResponseNotFound("Not a git-backed webapp")

    try:
        git_webapp = GitWebapp.objects.get(pk=webapp.pk)
    except GitWebapp.DoesNotExist:
        return HttpResponseNotFound("Git webapp not found")

    if not git_webapp.published_commit:
        return HttpResponseNotFound("No published version")

    client = get_forgejo_client()

    try:
        content = client.get_file(
            git_webapp.repository,
            path,
            git_webapp.published_commit,
            org_slug=git_webapp.org.slug,
        )
    except ForgejoAPIError as e:
        if e.status_code == 404:
            return HttpResponseNotFound("File not found")
        raise

    content_type, _ = mimetypes.guess_type(path)
    if not content_type:
        content_type = "application/octet-stream"

    return HttpResponse(content, content_type=content_type)
