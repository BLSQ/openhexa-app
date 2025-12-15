import base64

from django.http import HttpRequest

from hexa.utils.base64_image_encode_decode import decode_base64_image
from hexa.webapps.models import Webapp
from hexa.workspaces.base_workspace_mutation_type import BaseWorkspaceMutationType


def _decode_icon_if_present(input: dict):
    if input.get("icon"):
        input["icon"] = decode_base64_image(input["icon"])


def _flatten_webapp_content(input: dict):
    """
    Flatten the WebappContentInput structure to extract type and content fields.
    GraphQL's @oneOf ensures only one content type is provided.
    """
    content_input = input.get("content")
    if not content_input:
        return

    match content_input:
        case {"iframe": iframe_data}:
            input["type"] = "iframe"
            input["url"] = iframe_data["url"]
            del input["content"]
        case {"html": html_data}:
            input["type"] = "html"
            input["content"] = html_data["content"]
        case {"bundle": bundle_data}:
            input["type"] = "bundle"
            input["bundle"] = base64.b64decode(bundle_data["bundle"])
        case {"superset": superset_data}:
            input["type"] = "superset"
            input["url"] = superset_data["url"]
            del input["content"]
        case _:
            raise ValueError(
                f"Unknown webapp content type: {list(content_input.keys())}"
            )


class WebappsWorkspaceMutationType(BaseWorkspaceMutationType):
    def pre_create(self, request: HttpRequest, input: dict):
        input["created_by"] = request.user
        if not input.get("content"):
            raise ValueError("Content is required when creating a webapp")
        _flatten_webapp_content(input)
        _decode_icon_if_present(input)

    def pre_update(self, request: HttpRequest, instance, input: dict):
        _flatten_webapp_content(input)
        _decode_icon_if_present(input)


webapps_mutations = WebappsWorkspaceMutationType(Webapp)


@webapps_mutations.field("addToFavorites")
def resolve_add_to_favorites(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        webapp = Webapp.objects.get(pk=input["webapp_id"])
        webapp.add_to_favorites(request.user)
        return {"success": True, "errors": []}
    except Webapp.DoesNotExist:
        return {"success": False, "errors": "WEBAPP_NOT_FOUND"}


@webapps_mutations.field("removeFromFavorites")
def resolve_remove_from_favorites(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        webapp = Webapp.objects.get(pk=input["webapp_id"])
        webapp.remove_from_favorites(request.user)
        return {"success": True, "errors": []}
    except Webapp.DoesNotExist:
        return {"success": False, "errors": "WEBAPP_NOT_FOUND"}


bindables = [webapps_mutations]
