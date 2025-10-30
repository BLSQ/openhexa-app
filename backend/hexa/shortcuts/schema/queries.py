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

    webapp_content_type = ContentType.objects.get_for_model(Webapp)

    for shortcut in shortcuts:
        if shortcut.content_type == webapp_content_type:
            try:
                webapp = Webapp.objects.get(pk=shortcut.object_id)
                from hexa.utils.base64_image_encode_decode import encode_base64_image

                icon = encode_base64_image(bytes(webapp.icon)) if webapp.icon else None
                shortcut_items.append(
                    {
                        "id": str(webapp.id),
                        "name": webapp.name,
                        "url": f"/workspaces/{workspace.slug}/webapps/{webapp.id}",
                        "icon": icon,
                        "type": "webapp",
                        "order": shortcut.order,
                    }
                )
            except Webapp.DoesNotExist:
                continue

    return shortcut_items


bindables = [
    shortcut_query,
]
