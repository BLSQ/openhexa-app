from ariadne import ObjectType

from hexa.utils.base64_image_encode_decode import encode_base64_image
from hexa.webapps.models import Webapp

webapp_permissions = ObjectType("WebappPermissions")
webapp_object = ObjectType("Webapp")


@webapp_object.field("isFavorite")
def resolve_is_favorite(webapp: Webapp, info, **kwargs):
    request = info.context["request"]
    return webapp.is_favorite(request.user)


@webapp_object.field("isShortcut")
def resolve_is_shortcut(webapp: Webapp, info, **kwargs):
    request = info.context["request"]
    return webapp.is_shortcut(request.user)


@webapp_object.field("createdBy")
def resolve_created_by(webapp: Webapp, info, **kwargs):
    return webapp.created_by


@webapp_object.field("permissions")
def resolve_webapp_permissions(webapp, info, **kwargs):
    return webapp


@webapp_object.field("workspace")
def resolve_workspace(webapp: Webapp, info, **kwargs):
    return webapp.workspace


@webapp_object.field("url")
def resolve_url(webapp: Webapp, info, **kwargs):
    return webapp.url


@webapp_object.field("icon")
def resolve_icon(webapp: Webapp, info, **kwargs):
    return encode_base64_image(bytes(webapp.icon)) if webapp.icon else None


@webapp_object.field("description")
def resolve_description(webapp: Webapp, info, **kwargs):
    return webapp.description


@webapp_object.field("type")
def resolve_type(webapp: Webapp, info, **kwargs):
    return webapp.type.upper()


@webapp_object.field("isPublic")
def resolve_is_public(webapp: Webapp, info, **kwargs):
    return webapp.is_public


@webapp_permissions.field("update")
def resolve_webapp_permissions_update(obj, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "webapps.update_webapp", obj
    )


@webapp_permissions.field("delete")
def resolve_webapp_permissions_delete(obj, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "webapps.delete_webapp", obj
    )


bindables = [
    webapp_permissions,
    webapp_object,
]
