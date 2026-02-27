import io

from ariadne import MutationType

from hexa.analytics.api import track
from hexa.files import storage
from hexa.files.backends.exceptions import NotFound
from hexa.workspaces.models import Workspace

mutations = MutationType()


@mutations.field("deleteBucketObject")
def resolve_delete_bucket_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
        if not request.user.has_perm("files.delete_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        storage.delete_object(workspace.bucket_name, mutation_input["object_key"])
        return {"success": True, "errors": []}
    except (storage.exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("prepareObjectDownload")
def resolve_prepare_download_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
        if not request.user.has_perm("files.download_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}
        object_key = mutation_input["object_key"]
        download_url = storage.generate_download_url(
            bucket_name=workspace.bucket_name,
            target_key=object_key,
            force_attachment=mutation_input.get("force_attachment", True),
        )
        track(
            request,
            "files.download_url_generated",
            {"filename": object_key, "workspace": workspace.slug},
        )

        return {"success": True, "download_url": download_url, "errors": []}
    except (storage.exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("prepareObjectUpload")
def resolve_prepare_upload_object(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
        if not request.user.has_perm("files.create_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}
        object_key = mutation_input["object_key"]
        upload_url, headers = storage.generate_upload_url(
            bucket_name=workspace.bucket_name,
            target_key=object_key,
            content_type=mutation_input.get("content_type"),
        )

        return {
            "success": True,
            "upload_url": upload_url,
            "headers": headers,
            "errors": [],
        }
    except (storage.exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("createBucketFolder")
def resolve_create_bucket_folder(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
        if not request.user.has_perm("files.create_object", workspace):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}
        folder_key = mutation_input["folder_key"]
        folder_object = storage.create_bucket_folder(workspace.bucket_name, folder_key)

        return {"success": True, "folder": folder_object, "errors": []}
    except (storage.exceptions.NotFound, Workspace.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}


@mutations.field("writeFileContent")
def resolve_write_file_content(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]
    workspace_slug = mutation_input["workspace_slug"]
    file_path = mutation_input["file_path"]
    content = mutation_input["content"]
    overwrite = mutation_input.get("overwrite", False)

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}

    if not request.user.has_perm("files.create_object", workspace):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    if not overwrite:
        try:
            storage.get_bucket_object(workspace.bucket_name, file_path)
            return {"success": False, "errors": ["ALREADY_EXISTS"]}
        except NotFound:
            pass

    encoded = content.encode("utf-8")
    storage.save_object(workspace.bucket_name, file_path, io.BytesIO(encoded))
    return {
        "success": True,
        "errors": [],
        "file_path": file_path,
        "size": len(encoded),
    }


bindables = [
    mutations,
]
