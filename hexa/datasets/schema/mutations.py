from ariadne import MutationType
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from hexa.analytics.api import track
from hexa.files import storage
from hexa.pipelines.authentication import PipelineRunUser
from hexa.workspaces.models import Workspace

from ..api import generate_download_url, generate_upload_url, get_blob
from ..models import Dataset, DatasetLink, DatasetVersion, DatasetVersionFile

mutations = MutationType()


@mutations.field("createDataset")
def resolve_create_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
        dataset = Dataset.objects.create_if_has_perm(
            principal=request.user,
            workspace=workspace,
            name=mutation_input["name"],
            description=mutation_input["description"],
        )
        link = DatasetLink.objects.get(dataset=dataset, workspace=workspace)

        return {
            "success": True,
            "errors": [],
            "link": link,
            "dataset": dataset,
        }
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("updateDataset")
def resolve_update_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["dataset_id"]
        )

        dataset.update_if_has_perm(
            principal=request.user,
            **mutation_input,
        )
        return {"success": True, "errors": [], "dataset": dataset}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("deleteDataset")
def resolve_delete_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["id"]
        )

        dataset.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("createDatasetVersion")
def resolve_create_dataset_version(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["dataset_id"]
        )

        version = DatasetVersion.objects.create_if_has_perm(
            principal=request.user,
            dataset=dataset,
            name=mutation_input["name"],
            changelog=mutation_input.get("changelog"),
        )

        # Register dataset version creation event
        tracked_user = (
            request.user.pipeline_run.user
            if isinstance(request.user, PipelineRunUser)
            else request.user
        )
        track(
            request,
            "datasets.dataset_version_created",
            {
                "dataset_version": version.name,
                "dataset_id": dataset.slug,
                "creation_source": (
                    "SDK" if isinstance(request.user, PipelineRunUser) else "UI"
                ),
                "workspace": dataset.workspace.slug,
            },
            user=tracked_user,
        )

        return {"success": True, "errors": [], "version": version}
    except IntegrityError:
        return {"success": False, "errors": ["DUPLICATE_NAME"]}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("updateDatasetVersion")
def resolve_update_dataset_version(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        version = DatasetVersion.objects.filter_for_user(request.user).get(
            id=mutation_input["version_id"]
        )

        version.update_if_has_perm(principal=request.user, **mutation_input)

        return {"success": True, "errors": [], "version": version}
    except DatasetVersion.DoesNotExist:
        return {"success": False, "errors": ["VERSION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("deleteDatasetVersion")
def resolve_delete_dataset_version(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        version = DatasetVersion.objects.filter_for_user(request.user).get(
            id=mutation_input["version_id"]
        )

        version.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except DatasetVersion.DoesNotExist:
        return {"success": False, "errors": ["VERSION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("linkDataset")
def resolve_link_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        dataset = Dataset.objects.filter_for_user(request.user).get(
            id=mutation_input["dataset_id"]
        )
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )

        if not request.user.has_perm("datasets.link_dataset", (dataset, workspace)):
            raise PermissionDenied

        link = dataset.link(principal=request.user, workspace=workspace)

        return {"success": True, "errors": [], "link": link}
    except IntegrityError:
        return {"success": False, "errors": ["ALREADY_LINKED"]}
    except Dataset.DoesNotExist:
        return {"success": False, "errors": ["DATASET_NOT_FOUND"]}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("deleteDatasetLink")
def resolve_delete_dataset_share(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        link = DatasetLink.objects.filter_for_user(request.user).get(
            id=mutation_input["id"]
        )

        link.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except DatasetLink.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("generateDatasetUploadUrl")
def resolve_generate_upload_url(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        version = DatasetVersion.objects.filter_for_user(request.user).get(
            id=mutation_input["version_id"]
        )
        if version.id != version.dataset.latest_version.id:
            return {"success": False, "errors": ["LOCKED_VERSION"]}

        full_uri = version.get_full_uri(mutation_input["uri"])
        if get_blob(full_uri) is not None:
            return {"success": False, "errors": ["ALREADY_EXISTS"]}

        upload_url = generate_upload_url(full_uri, mutation_input["content_type"])

        return {"success": True, "errors": [], "upload_url": upload_url}
    except ValidationError:
        return {"success": False, "errors": ["INVALID_URI"]}
    except DatasetVersion.DoesNotExist:
        return {"success": False, "errors": ["VERSION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("createDatasetVersionFile")
def resolve_create_version_file(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        version = DatasetVersion.objects.filter_for_user(request.user).get(
            id=mutation_input["version_id"]
        )

        if version.id != version.dataset.latest_version.id:
            return {"success": False, "errors": ["LOCKED_VERSION"]}

        with transaction.atomic():
            file = None
            try:
                file = version.get_file_by_name(mutation_input["uri"])
                if get_blob(file.uri) is not None:
                    return {"success": False, "errors": ["ALREADY_EXISTS"]}
            except DatasetVersionFile.DoesNotExist:
                file = DatasetVersionFile.objects.create_if_has_perm(
                    principal=request.user,
                    dataset_version=version,
                    uri=version.get_full_uri(mutation_input["uri"]),
                    content_type=mutation_input["content_type"],
                )

            file.generate_metadata()
            return {
                "success": True,
                "errors": [],
                "file": file,
            }
    except ValidationError:
        return {"success": False, "errors": ["INVALID_URI"]}
    except DatasetVersion.DoesNotExist:
        return {"success": False, "errors": ["VERSION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("prepareVersionFileDownload")
def resolve_version_file_download(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        file = DatasetVersionFile.objects.filter_for_user(request.user).get(
            id=mutation_input["file_id"]
        )
        # We only get the file if the user or pipeline can see the dataset either by direct access or via a link.
        # FIXME: Implement a better permission system to be able to check if the pipeline can download the file.
        if not isinstance(request.user, PipelineRunUser) and not request.user.has_perm(
            "datasets.download_dataset_version", file.dataset_version
        ):
            raise PermissionDenied

        download_url = generate_download_url(file)
        if download_url is None:
            return {"success": False, "errors": ["FILE_NOT_UPLOADED"]}

        return {"success": True, "errors": [], "download_url": download_url}
    except (DatasetVersionFile.DoesNotExist, storage.exceptions.NotFound):
        return {"success": False, "errors": ["FILE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("pinDataset")
def resolve_pin_dataset(_, info, **kwargs):
    request = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        link = DatasetLink.objects.get(id=mutation_input["link_id"])

        if not request.user.has_perm("datasets.pin_dataset", link):
            raise PermissionDenied

        link.is_pinned = mutation_input["pinned"]
        link.save()

        return {"success": True, "errors": [], "link": link}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except DatasetLink.DoesNotExist:
        return {"success": False, "errors": ["LINK_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


bindables = [mutations]
