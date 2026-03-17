import logging

from ariadne import MutationType
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError, transaction
from django.http import HttpRequest

from hexa.git.forgejo import ForgejoAPIError
from hexa.superset.models import SupersetInstance
from hexa.utils.base64_image_encode_decode import decode_base64_image
from hexa.webapps.models import GitWebapp, SupersetWebapp, Webapp
from hexa.workspaces.models import Workspace

logger = logging.getLogger(__name__)

webapps_mutations = MutationType()


@webapps_mutations.field("createWebapp")
def resolve_create_webapp(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user = request.user
    input = kwargs["input"]
    source = input["source"]

    try:
        workspace = Workspace.objects.filter_for_user(user).get(
            slug=input["workspace_slug"]
        )
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"], "webapp": None}

    icon = decode_base64_image(input["icon"]) if input.get("icon") else None
    is_public = input.get("is_public", False)

    try:
        with transaction.atomic():
            if "superset" in source:
                if not workspace.organization:
                    return {
                        "success": False,
                        "errors": ["SUPERSET_NOT_CONFIGURED"],
                        "webapp": None,
                    }
                try:
                    superset_instance = SupersetInstance.objects.get(
                        id=source["superset"]["instance_id"],
                        organization=workspace.organization,
                    )
                except SupersetInstance.DoesNotExist:
                    return {
                        "success": False,
                        "errors": ["SUPERSET_INSTANCE_NOT_FOUND"],
                        "webapp": None,
                    }

                webapp = SupersetWebapp.create_if_has_perm(
                    principal=user,
                    workspace=workspace,
                    name=input["name"],
                    description=input.get("description", ""),
                    icon=icon,
                    is_public=is_public,
                    created_by=user,
                    superset_instance=superset_instance,
                    external_dashboard_id=source["superset"]["dashboard_id"],
                )
            elif "static" in source:
                files_input = source["static"]
                files = (
                    [{"path": f["path"], "content": f["content"]} for f in files_input]
                    if files_input
                    else None
                )

                webapp = GitWebapp.create_if_has_perm(
                    principal=user,
                    workspace=workspace,
                    name=input["name"],
                    description=input.get("description", ""),
                    icon=icon,
                    is_public=is_public,
                    created_by=user,
                    webapp_type=Webapp.WebappType.STATIC,
                    files=files,
                )
            else:
                webapp = Webapp.objects.create_if_has_perm(
                    user,
                    workspace,
                    name=input["name"],
                    description=input.get("description", ""),
                    icon=icon,
                    is_public=is_public,
                    created_by=user,
                    url=source["iframe"]["url"],
                )
            return {"success": True, "errors": [], "webapp": webapp}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"], "webapp": None}
    except ValidationError:
        return {"success": False, "errors": ["INVALID_URL"], "webapp": None}
    except IntegrityError:
        return {"success": False, "errors": ["ALREADY_EXISTS"], "webapp": None}


@webapps_mutations.field("updateWebapp")
def resolve_update_webapp(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user = request.user
    input = kwargs["input"]

    try:
        webapp = Webapp.objects.filter_for_user(user).get(id=input["id"])
    except Webapp.DoesNotExist:
        return {"success": False, "errors": ["WEBAPP_NOT_FOUND"], "webapp": None}

    if not user.has_perm("webapps.update_webapp", webapp):
        return {"success": False, "errors": ["PERMISSION_DENIED"], "webapp": None}

    source = input.get("source")
    if source and "superset" in source:
        if webapp.type != Webapp.WebappType.SUPERSET:
            return {"success": False, "errors": ["TYPE_MISMATCH"], "webapp": None}
        if not webapp.workspace.organization:
            return {
                "success": False,
                "errors": ["SUPERSET_NOT_CONFIGURED"],
                "webapp": None,
            }
        try:
            superset_instance = SupersetInstance.objects.get(
                id=source["superset"]["instance_id"],
                organization=webapp.workspace.organization,
            )
        except SupersetInstance.DoesNotExist:
            return {
                "success": False,
                "errors": ["SUPERSET_INSTANCE_NOT_FOUND"],
                "webapp": None,
            }

        webapp = SupersetWebapp.objects.get(pk=webapp.pk)
        webapp.update_dashboard(superset_instance, source["superset"]["dashboard_id"])
    elif source and "iframe" in source:
        if webapp.type != Webapp.WebappType.IFRAME:
            return {"success": False, "errors": ["TYPE_MISMATCH"], "webapp": None}
        try:
            URLValidator()(source["iframe"]["url"])
        except ValidationError:
            return {"success": False, "errors": ["INVALID_URL"], "webapp": None}
        webapp.url = source["iframe"]["url"]

    if "name" in input:
        webapp.name = input["name"]
    if "description" in input:
        webapp.description = input["description"]
    if "icon" in input:
        webapp.icon = decode_base64_image(input["icon"]) if input["icon"] else None
    if "is_public" in input:
        webapp.is_public = input["is_public"]

    if input.get("files") is not None or input.get("published_version_id") is not None:
        try:
            git_webapp = GitWebapp.objects.get(pk=webapp.pk)
        except GitWebapp.DoesNotExist:
            return {"success": False, "errors": ["TYPE_MISMATCH"], "webapp": None}

        if input.get("files") is not None:
            files = [
                {"path": f["path"], "content": f["content"]} for f in input["files"]
            ]
            try:
                git_webapp.save_files(files, "Update webapp content", user)
            except ForgejoAPIError as e:
                logger.error("Failed to save webapp files: %s", e)
                return {"success": False, "errors": ["SAVE_FAILED"], "webapp": None}

        if input.get("published_version_id") is not None:
            try:
                git_webapp.publish_version(input["published_version_id"])
            except ValueError:
                return {
                    "success": False,
                    "errors": ["VERSION_NOT_FOUND"],
                    "webapp": None,
                }

        webapp = git_webapp

    try:
        webapp.save()
        return {"success": True, "errors": [], "webapp": webapp}
    except IntegrityError:
        return {"success": False, "errors": ["ALREADY_EXISTS"], "webapp": None}


@webapps_mutations.field("deleteWebapp")
def resolve_delete_webapp(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user = request.user
    input = kwargs["input"]

    try:
        webapp = Webapp.objects.filter_for_user(user).get(id=input["id"])
    except Webapp.DoesNotExist:
        return {"success": False, "errors": ["WEBAPP_NOT_FOUND"]}

    try:
        webapp.delete_if_has_perm(principal=user)
        return {"success": True, "errors": []}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


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
