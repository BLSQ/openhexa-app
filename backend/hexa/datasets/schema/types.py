import logging

from ariadne import ObjectType
from django.db.models import Q
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.datasets.api import generate_download_url, generate_upload_url
from hexa.datasets.models import (
    Dataset,
    DatasetFileSample,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.files import storage
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_object, workspace_permissions

dataset_object = ObjectType("Dataset")
dataset_permissions = ObjectType("DatasetPermissions")
dataset_version_object = ObjectType("DatasetVersion")
dataset_version_permissions = ObjectType("DatasetVersionPermissions")
dataset_version_file_object = ObjectType("DatasetVersionFile")
dataset_version_file_result_object = ObjectType("CreateDatasetVersionFileResult")
dataset_link_object = ObjectType("DatasetLink")
dataset_link_permissions = ObjectType("DatasetLinkPermissions")


@dataset_link_permissions.field("delete")
def resolve_dataset_link_permissions_delete(obj: DatasetLink, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.delete_dataset_link", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_link_permissions.field("pin")
def resolve_dataset_link_permissions_pin(obj: DatasetLink, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.pin_dataset", obj)
        if request.user.is_authenticated
        else False
    )


@workspace_object.field("datasets")
def resolve_workspace_datasets(obj: Workspace, info, pinned=None, query=None, **kwargs):
    qs = DatasetLink.objects.filter(workspace=obj).order_by("-updated_at")

    if query is not None:
        qs = qs.filter(name__icontains=query)

    if pinned is not None:
        qs = qs.filter(is_pinned=pinned)

    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@workspace_permissions.field("createDataset")
def resolve_workspace_permissions_create_dataset(obj: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    # FIXME: This should support the PipelineRunUser
    return (
        request.user.has_perm("datasets.create_dataset", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_object.field("versions")
def resolve_dataset_versions(obj: Dataset, info, **kwargs):
    return result_page(
        obj.versions.all(),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@dataset_object.field("version")
def resolve_dataset_version(obj: Dataset, info, **kwargs):
    try:
        return obj.versions.get(id=kwargs["id"])
    except DatasetVersion.DoesNotExist:
        return None


@dataset_object.field("latestVersion")
def resolve_latest_version(obj: Dataset, info, **kwargs):
    return obj.latest_version


@dataset_object.field("links")
def resolve_dataset_links(obj: Dataset, info, **kwargs):
    return result_page(
        obj.links.filter(~Q(workspace=obj.workspace)).order_by("-updated_at"),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@dataset_object.field("permissions")
def resolve_dataset_permissions(obj: Dataset, info, **kwargs):
    return obj


@dataset_object.field("updatedAt")
def resolve_dataset_updated_at(obj: Dataset, info, **kwargs):
    return (
        max(obj.updated_at, obj.latest_version.updated_at)
        if obj.latest_version
        else obj.updated_at
    )


@dataset_link_object.field("permissions")
def resolve_dataset_link_permissions(obj: DatasetLink, info, **kwargs):
    return obj


@dataset_version_object.field("permissions")
def resolve_dataset_version_permissions(obj: DatasetVersion, info, **kwargs):
    return obj


@dataset_permissions.field("createVersion")
def resolve_dataset_permissions_create_version(obj: Dataset, info, **kwargs):
    request: HttpRequest = info.context["request"]
    # FIXME: This should support the PipelineRunUser
    return (
        request.user.has_perm("datasets.create_dataset_version", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_permissions.field("update")
def resolve_dataset_permissions_update(obj: Dataset, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.update_dataset", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_permissions.field("delete")
def resolve_dataset_permissions_delete(obj: Dataset, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.delete_dataset", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_version_permissions.field("download")
def resolve_dataset_version_permissions_download(obj: DatasetVersion, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.download_dataset_version", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_version_object.field("files")
def resolve_version_files(obj: DatasetVersion, info, **kwargs):
    return result_page(
        obj.files.all(),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@dataset_version_object.field("fileByName")
def resolve_file_by_name(obj: DatasetVersion, info, name, **kwargs):
    try:
        return obj.get_file_by_name(name)
    except DatasetVersionFile.DoesNotExist:
        return None


dataset_version_object.set_alias("description", "changelog")


@dataset_version_permissions.field("update")
def resolve_version_permissions_update(obj: DatasetVersion, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.update_dataset_version", obj)
        if request.user.is_authenticated
        else False
    )


@dataset_version_permissions.field("delete")
def resolve_version_permissions_delete(obj: DatasetVersion, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("datasets.delete_dataset_version", obj)
        if request.user.is_authenticated
        else False
    )


# We define specifically this field for backward compatibility with the old API
@dataset_version_file_result_object.field("uploadUrl")
def resolve_upload_url(obj, info, **kwargs):
    try:
        file = obj["file"]
        upload_url = generate_upload_url(file.uri, file.content_type)
        return upload_url
    except storage.exceptions.AlreadyExists as exc:
        logging.error(f"Upload URL generation failed: {exc.message}")
        return None


@dataset_version_file_object.field("fileSample")
def resolve_version_file_metadata(obj: DatasetVersionFile, info, **kwargs):
    try:
        return obj.sample_entry
    except DatasetFileSample.DoesNotExist:
        logging.error(f"No sample found for file {obj.filename} with id {obj.id}")
        return None


@dataset_version_file_object.field("downloadUrl")
def resolve_version_file_download_url(
    obj: DatasetVersionFile, info, attachment: bool = True, **kwargs
):
    request: HttpRequest = info.context["request"]
    if request.user.has_perm("datasets.download_dataset_version", obj.dataset_version):
        return generate_download_url(obj, force_attachment=attachment)


bindables = [
    dataset_object,
    dataset_permissions,
    dataset_version_object,
    dataset_version_permissions,
    dataset_link_permissions,
    dataset_version_file_object,
    dataset_version_file_result_object,
    dataset_link_object,
]
