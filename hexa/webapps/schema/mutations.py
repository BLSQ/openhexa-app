from django.http import HttpRequest

from hexa.utils.crud_mutation_type import CRUDMutationType
from hexa.webapps.models import Webapp

webapps_mutations = CRUDMutationType(Webapp)


def pre_create_webapp(request, input):
    input["created_by"] = request.user


webapps_mutations.set_field(
    f"create{Webapp.__name__}", webapps_mutations.create(pre_hook=pre_create_webapp)
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
