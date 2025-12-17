from ariadne import QueryType
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace

webapp_query = QueryType()


@webapp_query.field("webapp")
def resolve_webapp(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=kwargs["workspace_slug"]
        )
        return Webapp.objects.filter_for_user(request.user).get(
            workspace=workspace, slug=kwargs["slug"]
        )
    except (Webapp.DoesNotExist, Workspace.DoesNotExist):
        return None


@webapp_query.field("webapps")
def resolve_webapps(_, info, **kwargs):
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


@webapp_query.field("publicWebapp")
def resolve_public_webapp(_, info, **kwargs):
    try:
        workspace = Workspace.objects.filter(archived=False).get(
            slug=kwargs["workspace_slug"]
        )
        return Webapp.objects.filter(
            workspace=workspace, slug=kwargs["slug"], is_public=True
        ).first()
    except Workspace.DoesNotExist:
        return None


bindables = [
    webapp_query,
]
