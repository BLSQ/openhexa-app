from ariadne import QueryType
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest

from hexa.shortcuts.models import Shortcut
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace

shortcut_query = QueryType()


@shortcut_query.field("shortcuts")
def resolve_shortcuts(_, info, **kwargs):
    """
    Resolve shortcuts query - returns all shortcuts for a user in a workspace.
    Extensible design: add content types to filter_by_content_types() as needed.
    """
    request: HttpRequest = info.context["request"]
    workspace_slug = kwargs.get("workspace_slug")

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return []

    shortcuts = (
        Shortcut.objects.filter_for_user(request.user)
        .filter(workspace=workspace)
        .filter_by_content_types(Webapp)
        .select_related("content_type")
        .order_by("order", "created_at")
    )

    if not shortcuts.exists():
        return []

    webapp_content_type = ContentType.objects.get_for_model(Webapp)
    webapp_ids = [
        s.object_id for s in shortcuts if s.content_type == webapp_content_type
    ]

    shortcut_items = []

    if webapp_ids:
        webapps = {str(w.id): w for w in Webapp.objects.filter(id__in=webapp_ids)}

        for shortcut in shortcuts:
            if shortcut.content_type == webapp_content_type:
                webapp = webapps.get(str(shortcut.object_id))
                if webapp:
                    shortcut_items.append(webapp.to_shortcut_item(shortcut))

    return shortcut_items


bindables = [
    shortcut_query,
]
