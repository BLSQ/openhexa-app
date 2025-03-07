from django.http import HttpRequest

from hexa.utils.base64_image_encode_decode import decode_base64_image
from hexa.utils.base_mutation_type import BaseMutationType
from hexa.webapps.models import Webapp

webapps_mutations = BaseMutationType(Webapp.objects, Webapp.objects.get_queryset())


def pre_create_webapp(request, input):
    input["created_by"] = request.user


def pre_update_webapp(request, input):
    if "icon" in input and input["icon"] is not None:
        input["icon"] = decode_base64_image(input["icon"])


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
