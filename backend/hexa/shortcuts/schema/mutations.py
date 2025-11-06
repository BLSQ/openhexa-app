from ariadne import MutationType
from django.http import HttpRequest

from hexa.webapps.models import Webapp

shortcut_mutations = MutationType()


@shortcut_mutations.field("addWebappToShortcuts")
def resolve_add_webapp_to_shortcuts(_, info, **kwargs):
    """
    Add a webapp to user's shortcuts.
    """
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]

    try:
        webapp = Webapp.objects.filter_for_user(request.user).get(
            pk=input_data["webapp_id"]
        )
    except Webapp.DoesNotExist:
        return {"success": False, "errors": ["ITEM_NOT_FOUND"]}

    created = webapp.add_to_shortcuts(request.user)
    if created:
        return {"success": True, "errors": []}
    else:
        return {"success": False, "errors": ["ITEM_ALREADY_EXISTS"]}


@shortcut_mutations.field("removeWebappFromShortcuts")
def resolve_remove_webapp_from_shortcuts(_, info, **kwargs):
    """
    Remove a webapp from user's shortcuts.
    """
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]

    try:
        webapp = Webapp.objects.filter_for_user(request.user).get(
            pk=input_data["webapp_id"]
        )
    except Webapp.DoesNotExist:
        return {"success": False, "errors": ["ITEM_NOT_FOUND"]}

    webapp.remove_from_shortcuts(request.user)
    return {"success": True, "errors": []}


bindables = [shortcut_mutations]
