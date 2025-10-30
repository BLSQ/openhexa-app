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

    This resolver:
    1. Gets the workspace by slug
    2. Filters shortcuts for the current user and workspace
    3. Iterates through shortcuts and builds ShortcutItem objects
    4. Currently supports only Webapp type, but designed to be extensible
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
        .select_related("content_type")
        .order_by("order", "-created_at")
    )

    shortcut_items = []

    # Get content type for Webapp
    webapp_content_type = ContentType.objects.get_for_model(Webapp)

    for shortcut in shortcuts:
        # Currently only support webapps, but this is extensible
        if shortcut.content_type == webapp_content_type:
            try:
                webapp = Webapp.objects.get(pk=shortcut.object_id)
                shortcut_items.append(
                    {
                        "id": str(webapp.id),
                        "name": webapp.name,
                        "url": f"/workspaces/{workspace.slug}/webapps/{webapp.id}",
                        "icon": None,  # TODO: Add icon support
                        "type": "webapp",
                        "order": shortcut.order,
                    }
                )
            except Webapp.DoesNotExist:
                # Skip shortcuts pointing to deleted objects
                continue

    return shortcut_items


bindables = [
    shortcut_query,
]
