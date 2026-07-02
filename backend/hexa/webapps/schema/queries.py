from ariadne import QueryType
from django.conf import settings
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.git.exceptions import GitFileNotFound
from hexa.superset.models import SupersetInstance
from hexa.webapps.models import GitWebapp, Webapp, WebappFileBinaryError
from hexa.workspaces.models import Workspace

webapp_query = QueryType()


@webapp_query.field("webapp")
def resolve_webapp(_, info, **kwargs):
    if not settings.WEBAPPS_DOMAIN:
        return None

    request: HttpRequest = info.context["request"]
    try:
        workspace = Workspace.objects.get(slug=kwargs["workspace_slug"])
        webapp = Webapp.objects.get(workspace=workspace, slug=kwargs["slug"])

        if (
            webapp.is_public
            or Webapp.objects.filter_for_user(request.user)
            .filter(pk=webapp.pk)
            .exists()
        ):
            return webapp

        return None
    except (Webapp.DoesNotExist, Workspace.DoesNotExist):
        return None


@webapp_query.field("webapps")
def resolve_webapps(_, info, **kwargs):
    if not settings.WEBAPPS_DOMAIN:
        return result_page(queryset=Webapp.objects.none(), page=1)

    request: HttpRequest = info.context["request"]
    if kwargs.get("workspace_slug", None):
        try:
            ws = Workspace.objects.filter_for_user(request.user).get(
                slug=kwargs.get("workspace_slug")
            )
            qs = (
                Webapp.objects.filter_for_user(request.user)
                .filter(workspace=ws)
                .order_by("name", "id")
            )
        except Workspace.DoesNotExist:
            qs = Webapp.objects.none()
    else:
        qs = Webapp.objects.filter_for_user(request.user).order_by("name", "id")

    if kwargs.get("favorite", None):
        qs = qs.filter_favorites(request.user)

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@webapp_query.field("readWebappFile")
def resolve_read_webapp_file(_, info, **kwargs):
    if not settings.WEBAPPS_DOMAIN:
        return {"success": False, "errors": ["WEBAPPS_NOT_CONFIGURED"]}

    request: HttpRequest = info.context["request"]
    try:
        webapp = GitWebapp.objects.filter_for_user(request.user).get(
            workspace__slug=kwargs["workspace_slug"], slug=kwargs["webapp_slug"]
        )
    except GitWebapp.DoesNotExist:
        return {"success": False, "errors": ["WEBAPP_NOT_FOUND"]}

    path = kwargs["path"]
    try:
        content = webapp.get_file_content(path)
    except GitFileNotFound:
        return {"success": False, "errors": ["PATH_NOT_FOUND"]}
    except WebappFileBinaryError:
        return {"success": False, "errors": ["BINARY_FILE"]}

    result = {"success": True, "errors": [], "path": path, "content": content}
    start_line = kwargs.get("start_line")
    end_line = kwargs.get("end_line")
    if start_line is not None or end_line is not None:
        all_lines = content.splitlines()
        total = len(all_lines)
        start = max(1, start_line or 1) - 1
        end = min(total, end_line or total)
        result.update(
            content="\n".join(all_lines[start:end]),
            start_line=start + 1,
            end_line=end,
            total_lines=total,
        )
    return result


@webapp_query.field("supersetInstances")
def resolve_superset_instances(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=kwargs["workspace_slug"]
        )
        if not workspace.organization:
            return []
        return SupersetInstance.objects.filter(organization=workspace.organization)
    except Workspace.DoesNotExist:
        return []


bindables = [
    webapp_query,
]
