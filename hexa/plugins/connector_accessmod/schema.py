import pathlib

from ariadne import (
    InterfaceType,
    MutationType,
    ObjectType,
    QueryType,
    load_schema_from_path,
)
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.urls import reverse
from django_countries.fields import Country
from slugify import slugify
from stringcase import snakecase

from config import settings
from hexa.core import mimetypes
from hexa.core.graphql import result_page
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    Analysis,
    File,
    Fileset,
    FilesetRole,
    GeographicCoverageAnalysis,
    Project,
)
from hexa.plugins.connector_s3.api import generate_download_url, generate_upload_url
from hexa.plugins.connector_s3.models import Bucket

accessmod_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
accessmod_query = QueryType()
accessmod_mutations = MutationType()


@accessmod_query.field("accessmodProject")
def resolve_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Project.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Project.DoesNotExist:
        return None


@accessmod_query.field("accessmodProjects")
def resolve_accessmod_projects(_, info, term=None, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = Project.objects.filter_for_user(request.user)

    if term is not None:
        queryset = queryset.filter(name__icontains=term)

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@accessmod_mutations.field("createAccessmodProject")
@transaction.atomic
def resolve_create_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    try:
        project = Project.objects.create(
            author=request.user,
            name=create_input["name"],
            country=Country(create_input["country"]["code"]),
            spatial_resolution=create_input["spatialResolution"],
            crs=create_input["crs"],
            extent=Fileset.objects.filter_for_user(request.user).get(
                id=create_input["filesetId"]
            )
            if "extentId" in create_input
            else None,
        )
        return {"success": True, "project": project, "errors": []}
    except IntegrityError:
        return {"success": False, "project": None, "errors": ["NAME_DUPLICATE"]}


@accessmod_mutations.field("updateAccessmodProject")
@transaction.atomic
def resolve_update_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(request.user).get(
            id=update_input["id"]
        )
        changed = False
        for scalar_field in ["name", "spatialResolution", "crs"]:
            if scalar_field in update_input:
                setattr(project, snakecase(scalar_field), update_input[scalar_field])
                changed = True
        if "extentId" in update_input:
            fileset = Fileset.objects.filter_for_user(request.user).get(
                id=update_input["extentId"]
            )
            project.extent = fileset
            changed = True
        if "country" in update_input:
            project.country = update_input["country"]["code"]
            changed = True
        if changed:
            try:
                project.save()
            except IntegrityError:
                return {
                    "success": False,
                    "project": project,
                    "errors": ["NAME_DUPLICATE"],
                }

        return {"success": True, "project": project, "errors": []}
    except Project.DoesNotExist:
        return {"success": False, "project": None, "errors": ["NOT_FOUND"]}


@accessmod_mutations.field("deleteAccessmodProject")
@transaction.atomic
def resolve_delete_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(request.user).get(
            id=update_input["id"]
        )
        project.delete()

        return {"success": True, "errors": []}
    except Project.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


fileset_object = ObjectType("AccessmodFileset")


@fileset_object.field("files")
def resolve_accessmod_fileset_files(fileset: Fileset, info, **kwargs):
    return [f for f in fileset.file_set.all()]


@accessmod_query.field("accessmodFileset")
def resolve_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Fileset.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Fileset.DoesNotExist:
        return None


@accessmod_query.field("accessmodFilesets")
def resolve_accessmod_filesets(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = (
        Fileset.objects.filter_for_user(request.user)
        .filter(project_id=kwargs["projectId"])
        .order_by("-created_at")
    )
    if "roleId" in kwargs:
        queryset = queryset.filter(role__id=kwargs["roleId"])
    if "term" in kwargs:
        queryset = queryset.filter(name__icontains=kwargs["term"])

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@accessmod_mutations.field("createAccessmodFileset")
@transaction.atomic
def resolve_create_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    try:
        fileset = Fileset.objects.create(
            author=request.user,
            name=create_input["name"],
            project=Project.objects.filter_for_user(request.user).get(
                id=create_input["projectId"]
            ),
            role=FilesetRole.objects.get(id=create_input["roleId"]),
        )
        return {"success": True, "fileset": fileset, "errors": []}
    except IntegrityError:
        return {"success": False, "fileset": None, "errors": ["NAME_DUPLICATE"]}


@accessmod_mutations.field("deleteAccessmodFileset")
@transaction.atomic
def resolve_delete_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    delete_input = kwargs["input"]
    try:
        fileset = Fileset.objects.filter_for_user(request.user).get(
            id=delete_input["id"]
        )
        fileset.delete()
        return {"success": True, "errors": []}
    except Fileset.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


@accessmod_mutations.field("prepareAccessmodFileUpload")
@transaction.atomic
def resolve_prepare_accessmod_file_upload(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    prepare_input = kwargs["input"]
    fileset = Fileset.objects.filter_for_user(request.user).get(
        id=prepare_input["filesetId"]
    )

    # This is a temporary solution until we figure out storage requirements
    if settings.ACCESSMOD_S3_BUCKET_NAME is None:
        raise ValueError("ACCESSMOD_S3_BUCKET_NAME is not set")
    try:
        bucket = Bucket.objects.get(name=settings.ACCESSMOD_S3_BUCKET_NAME)
    except Bucket.DoesNotExist:
        raise ValueError(
            f"The {settings.ACCESSMOD_S3_BUCKET_NAME} bucket does not exist"
        )
    target_slug = slugify(fileset.name, separator="_")
    target_key = f"{fileset.project.id}/{target_slug}{mimetypes.guess_extension(prepare_input['mimeType'])}"
    upload_url = generate_upload_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        target_key=target_key,
    )

    return {
        "success": True,
        "upload_url": upload_url,
        "file_uri": f"s3://{bucket.name}/{target_key}",
    }


@accessmod_mutations.field("prepareAccessmodFileDownload")
@transaction.atomic
def resolve_prepare_accessmod_file_download(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    prepare_input = kwargs["input"]
    file = File.objects.filter_for_user(request.user).get(id=prepare_input["fileId"])

    # This is a temporary solution until we figure out storage requirements
    if settings.ACCESSMOD_S3_BUCKET_NAME is None:
        raise ValueError("ACCESSMOD_S3_BUCKET_NAME is not set")
    try:
        bucket = Bucket.objects.get(name=settings.ACCESSMOD_S3_BUCKET_NAME)
    except Bucket.DoesNotExist:
        raise ValueError(
            f"The {settings.ACCESSMOD_S3_BUCKET_NAME} bucket does not exist"
        )
    download_url = generate_download_url(
        principal_credentials=bucket.principal_credentials,
        bucket=bucket,
        # Ugly workaround, TBD when we know more about storage
        target_key=file.uri.replace(f"s3://{bucket.name}/", ""),
    )

    return {
        "success": True,
        "download_url": download_url,
    }


@accessmod_mutations.field("createAccessmodFile")
@transaction.atomic
def resolve_create_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    fileset = Fileset.objects.filter_for_user(request.user).get(
        id=create_input["filesetId"]
    )
    try:
        file = File.objects.create(
            uri=create_input["uri"],
            mime_type=create_input["mimeType"],
            fileset=fileset,
        )
        fileset.save()  # Will update updated_at
        return {"success": True, "file": file, "errors": []}
    except IntegrityError:
        return {"success": False, "file": None, "errors": ["URI_DUPLICATE"]}


@accessmod_mutations.field("deleteAccessmodFile")
@transaction.atomic
def resolve_delete_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    delete_input = kwargs["input"]
    try:
        file = File.objects.filter_for_user(request.user).get(id=delete_input["id"])
        fileset = file.fileset
        file.delete()
        fileset.save()  # Will update updated_at
        return {"success": True, "errors": []}
    except File.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


@accessmod_query.field("accessmodFilesetRole")
def resolve_accessmod_fileset_role(_, info, **kwargs):
    try:
        return FilesetRole.objects.get(id=kwargs["id"])
    except FilesetRole.DoesNotExist:
        return None


@accessmod_query.field("accessmodFilesetRoles")
def resolve_accessmod_fileset_roles(_, info, **kwargs):
    return FilesetRole.objects.all()


analysis_interface = InterfaceType("AccessmodAnalysis")


@analysis_interface.type_resolver
def resolve_analysis_type(analysis: Analysis, *_):
    if isinstance(analysis, AccessibilityAnalysis):
        return "AccessmodAccessibilityAnalysis"
    elif isinstance(analysis, GeographicCoverageAnalysis):
        return "AccessmodGeographicCoverageAnalysis"

    return None


@accessmod_query.field("accessmodAnalysis")
def resolve_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Analysis.objects.filter_for_user(request.user).get_subclass(
            id=kwargs["id"]
        )
    except Analysis.DoesNotExist:
        return None


@accessmod_query.field("accessmodAnalyses")
def resolve_accessmod_analyses(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = (
        Analysis.objects.filter_for_user(request.user)
        .filter(project_id=kwargs["projectId"])
        .order_by("-created_at")
        .select_subclasses()
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@accessmod_mutations.field("createAccessmodAccessibilityAnalysis")
@transaction.atomic
def resolve_create_accessmod_accessibility_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    try:
        analysis = AccessibilityAnalysis.objects.create(
            author=request.user,
            project=Project.objects.filter_for_user(request.user).get(
                id=create_input["projectId"]
            ),
            name=create_input["name"],
        )
        return {"success": True, "analysis": analysis, "errors": []}
    except IntegrityError:
        return {"success": False, "analysis": None, "errors": ["NAME_DUPLICATE"]}


@accessmod_mutations.field("updateAccessmodAccessibilityAnalysis")
@transaction.atomic
def resolve_update_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        analysis = Analysis.objects.filter_for_user(request.user).get_subclass(
            id=update_input["id"]
        )
        changed = False
        for scalar_field in [
            "name",
            "invertDirection",
            "maxTravelTime",
            "maxSlope",
            "priorityRoads",
            "priorityLandCover",
            "waterAllTouched",
            "algorithm",
            "knightMove",
        ]:
            if scalar_field in update_input:
                setattr(analysis, snakecase(scalar_field), update_input[scalar_field])
                changed = True
        for fileset_field in [
            "landCoverId",
            "demId",
            "transportNetworkId",
            "slopeId",
            "waterId",
            "barrierId",
            "movingSpeedsId",
            "healthFacilitiesId",
        ]:
            if fileset_field in update_input:
                fileset = Fileset.objects.filter_for_user(request.user).get(
                    id=update_input[fileset_field]
                )
                setattr(analysis, snakecase(fileset_field), fileset.id)
                changed = True
        if changed:
            try:
                analysis.save()
            except IntegrityError:
                return {
                    "success": False,
                    "analysis": analysis,
                    "errors": ["NAME_DUPLICATE"],
                }

        return {"success": True, "analysis": analysis, "errors": []}
    except Analysis.DoesNotExist:
        return {"success": False, "analysis": None, "errors": ["NOT_FOUND"]}


@accessmod_mutations.field("launchAccessmodAnalysis")
@transaction.atomic
def resolve_launch_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    launch_input = kwargs["input"]
    analysis = Analysis.objects.filter_for_user(request.user).get_subclass(
        id=launch_input["id"]
    )

    try:
        analysis.run(
            request=request, webhook_path=reverse("connector_accessmod:webhook")
        )
        return {"success": True, "analysis": analysis, "errors": []}
    except ValueError:
        return {"success": False, "analysis": analysis, "errors": ["LAUNCH_FAILED"]}


@accessmod_mutations.field("deleteAccessmodAnalysis")
@transaction.atomic
def resolve_delete_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    delete_input = kwargs["input"]

    try:
        analysis = Analysis.objects.filter_for_user(request.user).get_subclass(
            id=delete_input["id"]
        )
        analysis.delete()
        return {"success": True, "errors": []}
    except Analysis.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except ValueError:
        return {"success": False, "errors": ["DELETE_FAILED"]}


accessmod_bindables = [
    accessmod_query,
    accessmod_mutations,
    fileset_object,
    analysis_interface,
]
