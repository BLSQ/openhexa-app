from ariadne import MutationType

from hexa.core.analytics import track
from hexa.files.api import get_storage
from hexa.workspaces.models import Workspace

mutations = MutationType()


@mutations.field("deleteBucketObject")
def resolve_delete_bucket_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspaceSlug"]
        )
        if not request.user.has_perm("files.delete_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        get_storage().delete_object(workspace.bucket_name, mutation_input["objectKey"])
        return {"success": True, "errors": []}
    except (get_storage().exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("prepareObjectDownload")
def resolve_prepare_download_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspaceSlug"]
        )
        if not request.user.has_perm("files.download_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}
        object_key = mutation_input["objectKey"]
        download_url = get_storage().generate_download_url(
            workspace.bucket_name, object_key, force_attachment=True
        )
        track(
            request,
            "files.download_url_generated",
            {"filename": object_key, "workspace": workspace.slug},
        )

        return {"success": True, "download_url": download_url, "errors": []}
    except (get_storage().exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("prepareObjectUpload")
def resolve_prepare_upload_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspaceSlug"]
        )
        if not request.user.has_perm("files.create_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}
        object_key = mutation_input["objectKey"]
        upload_url = get_storage().generate_upload_url(
            workspace.bucket_name, object_key, mutation_input.get("contentType")
        )

        return {"success": True, "upload_url": upload_url, "errors": []}
    except (get_storage().exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("createBucketFolder")
def resolve_create_bucket_folder(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspaceSlug"]
        )
        if not request.user.has_perm("files.create_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}
        folder_key = mutation_input["folderKey"]
        folder_object = get_storage().create_bucket_folder(
            workspace.bucket_name, folder_key
        )

        return {"success": True, "folder": folder_object, "errors": []}
    except (get_storage().exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


bindables = [
    mutations,
]
