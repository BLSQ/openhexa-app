from django.http import HttpRequest

from hexa.utils.base64_image_encode_decode import decode_base64_image
from hexa.utils.base_mutation_type import BaseMutationType
from hexa.webapps.models import Webapp


# TODO : ensure the model is passed or the manager and queryset are from the same model
# TODO : move class to workspace folder
def _decode_icon_if_present(input: dict):
    if input.get("icon"):
        input["icon"] = decode_base64_image(input["icon"])


class WebappsMutationType(BaseMutationType):
    def pre_create(self, request: HttpRequest, input: dict):
        input["created_by"] = request.user
        _decode_icon_if_present(input)

    def perform_update(self, request: HttpRequest, instance, input: dict):
        _decode_icon_if_present(input)


webapps_mutations = WebappsMutationType(Webapp.objects, Webapp.objects.get_queryset())


def pre_update_webapp(request, input):
    if input.get("icon"):
        input["icon"] = decode_base64_image(input["icon"])


def pre_create_webapp(request, input):
    input["created_by"] = request.user
    pre_update_webapp(request, input)


webapps_mutations.set_field(
    f"create{Webapp.__name__}", webapps_mutations.create(pre_hook=pre_create_webapp)
)

webapps_mutations.set_field(
    f"update{Webapp.__name__}", webapps_mutations.update(pre_hook=pre_update_webapp)
)


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
