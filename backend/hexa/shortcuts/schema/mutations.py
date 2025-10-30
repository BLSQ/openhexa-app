from ariadne import MutationType
from django.db import IntegrityError
from django.http import HttpRequest

from hexa.webapps.models import Webapp

shortcut_mutations = MutationType()


@shortcut_mutations.field("addToShortcuts")
def resolve_add_to_shortcuts(_, info, **kwargs):
    """
    Add a webapp to user's shortcuts.
    """
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]

    try:
        webapp = Webapp.objects.filter_for_user(request.user).get(
            pk=input_data["webapp_id"]
        )
        webapp.add_to_shortcuts(request.user)
        return {"success": True, "errors": []}
    except Webapp.DoesNotExist:
        return {"success": False, "errors": ["ITEM_NOT_FOUND"]}
    except IntegrityError:
        return {"success": True, "errors": []}
    except Exception:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@shortcut_mutations.field("removeFromShortcuts")
def resolve_remove_from_shortcuts(_, info, **kwargs):
    """
    Remove a webapp from user's shortcuts.
    """
    request: HttpRequest = info.context["request"]
    input_data = kwargs["input"]

    try:
        webapp = Webapp.objects.filter_for_user(request.user).get(
            pk=input_data["webapp_id"]
        )
        webapp.remove_from_shortcuts(request.user)
        return {"success": True, "errors": []}
    except Webapp.DoesNotExist:
        return {"success": False, "errors": ["ITEM_NOT_FOUND"]}
    except Exception:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


bindables = [shortcut_mutations]
