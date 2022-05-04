import pathlib

from ariadne import (
    EnumType,
    InterfaceType,
    MutationType,
    ObjectType,
    QueryType,
    UnionType,
    load_schema_from_path,
)
from django.core.exceptions import PermissionDenied
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
    ProjectPermission,
)
from hexa.plugins.connector_accessmod.queue import validate_fileset_queue
from hexa.plugins.connector_s3.api import generate_download_url, generate_upload_url
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import Team, User

accessmod_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
accessmod_query = QueryType()
accessmod_mutations = MutationType()

# Projects
project_object = ObjectType("AccessmodProject")

project_order_by = EnumType(
    "AccessmodProjectOrder",
    {
        "UPDATED_AT_DESC": "-updated_at",
        "UPDATED_AT_ASC": "updated_at",
        "NAME_DESC": "-name",
        "NAME_ASC": "name",
    },
)

owner_union = UnionType("AccessmodOwner")


@owner_union.type_resolver
def resolve_accessmod_owner_type(obj, *_):
    if isinstance(obj, Team):
        return "Team"
    elif isinstance(obj, User):
        return "User"


ownership_interface = InterfaceType("AccessmodOwnership")


@ownership_interface.type_resolver
def resolve_ownership_type(obj, *_):
    if isinstance(obj, AccessibilityAnalysis):
        return "AccessmodAccessibilityAnalysis"
    elif isinstance(obj, GeographicCoverageAnalysis):
        return "AccessmodGeographicCoverageAnalysis"
    elif isinstance(obj, Project):
        return "AccessmodProject"
    elif isinstance(obj, Fileset):
        return "AccessmodFileset"


@project_object.field("authorizedActions")
def resolve_accessmod_project_authorized_actions(project: Project, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    return filter(
        bool,
        [
            "UPDATE"
            if principal.has_perm("connector_accessmod.update_project", project)
            else None,
            "DELETE"
            if principal.has_perm("connector_accessmod.delete_project", project)
            else None,
            "CREATE_FILESET"
            if principal.has_perm("connector_accessmod.create_fileset", project)
            else None,
            "CREATE_ANALYSIS"
            if principal.has_perm("connector_accessmod.create_analysis", project)
            else None,
            "CREATE_PERMISSION"
            if principal.has_perm(
                "connector_accessmod.create_project_permission", project
            )
            else None,
        ],
    )


@project_object.field("permissions")
def resolve_accessmod_project_permissions(project: Project, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    return project.projectpermission_set.filter_for_user(principal).all()


@accessmod_query.field("accessmodProject")
def resolve_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Project.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Project.DoesNotExist:
        return None


@accessmod_query.field("accessmodProjects")
def resolve_accessmod_projects(
    _, info, term=None, countries=None, teams=None, **kwargs
):
    request: HttpRequest = info.context["request"]

    queryset = Project.objects.filter_for_user(request.user)

    if term is not None:
        queryset = queryset.filter(name__icontains=term)

    if countries is not None and len(countries) > 0:
        queryset = queryset.filter(country__in=countries)

    if teams is not None and len(teams) > 0:
        queryset = queryset.filter(projectpermission__team__id__in=teams)

    order_by = kwargs.get("orderBy", None)
    if order_by is not None:
        queryset = queryset.order_by(order_by)

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@accessmod_mutations.field("createAccessmodProject")
@transaction.atomic
def resolve_create_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        project = Project.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
            country=Country(create_input["country"]["code"]),
            spatial_resolution=create_input["spatialResolution"],
            crs=create_input["crs"],
            description=create_input.get("description", ""),
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
    principal = request.user
    update_input = kwargs["input"]

    try:
        project: Project = Project.objects.filter_for_user(principal).get(
            id=update_input["id"]
        )
        changes = {}
        for scalar_field in ["name", "spatialResolution", "crs", "description"]:
            if scalar_field in update_input:
                changes[snakecase(scalar_field)] = update_input[scalar_field]
        if "extentId" in update_input:
            fileset = Fileset.objects.filter_for_user(principal).get(
                id=update_input["extentId"]
            )
            changes["extent"] = fileset
        if "demId" in update_input:
            dem = Fileset.objects.filter_for_user(principal).get(
                id=update_input["demId"]
            )
            changes["dem"] = dem
        if "country" in update_input:
            changes["country"] = update_input["country"]["code"]
        if len(changes) > 0:
            try:
                project.update_if_has_perm(principal, **changes)
            except IntegrityError:
                return {
                    "success": False,
                    "project": None,
                    "errors": ["NAME_DUPLICATE"],
                }
            except PermissionDenied:
                return {
                    "success": False,
                    "project": None,
                    "errors": ["PERMISSION_DENIED"],
                }

        return {"success": True, "project": project, "errors": []}
    except Project.DoesNotExist:
        return {"success": False, "project": None, "errors": ["NOT_FOUND"]}


@accessmod_mutations.field("deleteAccessmodProject")
@transaction.atomic
def resolve_delete_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(principal).get(id=update_input["id"])
        project.delete_if_has_perm(principal)

        return {"success": True, "errors": []}
    except Project.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


# Permissions
permission_object = ObjectType("AccessmodProjectPermission")


@permission_object.field("authorizedActions")
def resolve_accessmod_project_permission_authorized_actions(
    permission: ProjectPermission, info, **kwargs
):
    request: HttpRequest = info.context["request"]
    principal = request.user

    return filter(
        bool,
        [
            "UPDATE"
            if principal.has_perm(
                "connector_accessmod.update_project_permission", permission
            )
            else None,
            "DELETE"
            if principal.has_perm(
                "connector_accessmod.delete_project_permission", permission
            )
            else None,
        ],
    )


@accessmod_mutations.field("createAccessmodProjectPermission")
@transaction.atomic
def resolve_create_accessmod_project_permission(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        user = (
            User.objects.get(id=create_input["userId"])
            if "userId" in create_input
            else None
        )
        team = (
            Team.objects.get(id=create_input["teamId"])
            if "teamId" in create_input
            else None
        )
        project = Project.objects.get(pk=create_input["projectId"])

        try:
            permission: ProjectPermission = ProjectPermission.objects.get(
                project=project, user=user, team=team
            )
            permission.update_if_has_perm(principal, mode=create_input["mode"])
        except ProjectPermission.DoesNotExist:
            permission = ProjectPermission.objects.create_if_has_perm(
                principal,
                project=project,
                user=user,
                team=team,
                mode=create_input["mode"],
            )
        return {"success": True, "permission": permission, "errors": []}
    except (Team.DoesNotExist, User.DoesNotExist, Project.DoesNotExist):
        return {"success": False, "permission": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "permission": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("updateAccessmodProjectPermission")
@transaction.atomic
def resolve_update_accessmod_project_permission(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        permission = ProjectPermission.objects.filter_for_user(user=principal).get(
            id=update_input["id"]
        )
        permission.update_if_has_perm(principal, mode=update_input["mode"])

        return {"success": True, "permission": permission, "errors": []}
    except ProjectPermission.DoesNotExist:
        return {"success": False, "permission": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "permission": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("deleteAccessmodProjectPermission")
@transaction.atomic
def resolve_delete_accessmod_project_permission(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        permission = ProjectPermission.objects.filter_for_user(user=principal).get(
            id=delete_input["id"]
        )
        permission.delete_if_has_perm(principal)

        return {"success": True, "errors": []}
    except ProjectPermission.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


# Filesets
fileset_object = ObjectType("AccessmodFileset")


@fileset_object.field("files")
def resolve_accessmod_fileset_files(fileset: Fileset, info, **kwargs):
    return [f for f in fileset.file_set.all()]


@fileset_object.field("authorizedActions")
def resolve_accessmod_fileset_authorized_actions(fileset: Fileset, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    return filter(
        bool,
        [
            "UPDATE"
            if principal.has_perm("connector_accessmod.update_fileset", fileset)
            else None,
            "DELETE"
            if principal.has_perm("connector_accessmod.delete_fileset", fileset)
            else None,
            "CREATE_FILE"
            if principal.has_perm("connector_accessmod.create_file", fileset)
            else None,
        ],
    )


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
    principal = request.user
    create_input = kwargs["input"]

    try:
        fileset = Fileset.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
            project=Project.objects.filter_for_user(request.user).get(
                id=create_input["projectId"]
            ),
            role=FilesetRole.objects.get(id=create_input["roleId"]),
        )
        return {"success": True, "fileset": fileset, "errors": []}
    except IntegrityError:
        return {"success": False, "fileset": None, "errors": ["NAME_DUPLICATE"]}
    except PermissionDenied:
        return {"success": False, "fileset": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("deleteAccessmodFileset")
@transaction.atomic
def resolve_delete_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        fileset = Fileset.objects.filter_for_user(principal).get(id=delete_input["id"])
        fileset.delete_if_has_perm(principal)
        return {"success": True, "errors": []}
    except Fileset.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("prepareAccessmodFileUpload")
@transaction.atomic
def resolve_prepare_accessmod_file_upload(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    prepare_input = kwargs["input"]
    fileset = Fileset.objects.filter_for_user(principal).get(
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
    principal = request.user
    prepare_input = kwargs["input"]
    file = File.objects.filter_for_user(principal).get(id=prepare_input["fileId"])

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
    principal = request.user
    create_input = kwargs["input"]

    fileset = Fileset.objects.filter_for_user(principal).get(
        id=create_input["filesetId"]
    )
    try:
        file = File.objects.create_if_has_perm(
            principal,
            uri=create_input["uri"],
            mime_type=create_input["mimeType"],
            fileset=fileset,
        )
        fileset.save()  # Will update updated_at

        # start background validation
        validate_fileset_queue.enqueue(
            "validate_fileset",
            {
                "fileset_id": str(fileset.id),
            },
        )
        return {"success": True, "file": file, "errors": []}
    except IntegrityError:
        return {"success": False, "file": None, "errors": ["URI_DUPLICATE"]}
    except PermissionDenied:
        return {"success": False, "file": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("deleteAccessmodFile")
@transaction.atomic
def resolve_delete_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        file = File.objects.filter_for_user(principal).get(id=delete_input["id"])
        fileset = file.fileset
        file.delete_if_has_perm()
        fileset.save()  # Will update updated_at
        return {"success": True, "errors": []}
    except File.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


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


# Analysis
@analysis_interface.field("authorizedActions")
def resolve_accessmod_analysis_authorized_actions(analysis: Analysis, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    return filter(
        bool,
        [
            "UPDATE"
            if principal.has_perm("connector_accessmod.update_analysis", analysis)
            else None,
            "DELETE"
            if principal.has_perm("connector_accessmod.delete_analysis", analysis)
            else None,
            "RUN"
            if principal.has_perm("connector_accessmod.run_analysis", analysis)
            else None,
        ],
    )


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
    principal = request.user
    create_input = kwargs["input"]

    try:
        analysis = AccessibilityAnalysis.objects.create_if_has_perm(
            principal,
            project=Project.objects.filter_for_user(request.user).get(
                id=create_input["projectId"]
            ),
            name=create_input["name"],
        )
        return {"success": True, "analysis": analysis, "errors": []}
    except IntegrityError:
        return {"success": False, "analysis": None, "errors": ["NAME_DUPLICATE"]}
    except PermissionDenied:
        return {"success": False, "analysis": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("updateAccessmodAccessibilityAnalysis")
@transaction.atomic
def resolve_update_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        analysis = Analysis.objects.filter_for_user(principal).get_subclass(
            id=update_input["id"]
        )
        changes = {}
        for scalar_field in [
            "name",
            "invertDirection",
            "maxTravelTime",
            "maxSlope",
            "waterAllTouched",
            "algorithm",
            "knightMove",
        ]:
            if scalar_field in update_input:
                changes[snakecase(scalar_field)] = update_input[scalar_field]

        if "priorities" in update_input:
            changes["stack_priorities"] = update_input["priorities"]

        for fileset_field in [
            "landCoverId",
            "demId",
            "stackId",
            "transportNetworkId",
            "slopeId",
            "waterId",
            "barrierId",
            "movingSpeedsId",
            "healthFacilitiesId",
        ]:
            if fileset_field in update_input:
                fileset = Fileset.objects.filter_for_user(principal).get(
                    id=update_input[fileset_field]
                )
                changes[snakecase(fileset_field)] = fileset.id
        if len(changes) > 0:
            try:
                analysis.update_if_has_perm(principal, **changes)
            except IntegrityError:
                return {
                    "success": False,
                    "analysis": analysis,
                    "errors": ["NAME_DUPLICATE"],
                }
            except PermissionDenied:
                return {
                    "success": False,
                    "analysis": analysis,
                    "errors": ["PERMISSION_DENIED"],
                }

        return {"success": True, "analysis": analysis, "errors": []}
    except Analysis.DoesNotExist:
        return {"success": False, "analysis": None, "errors": ["NOT_FOUND"]}


@accessmod_mutations.field("launchAccessmodAnalysis")
@transaction.atomic
def resolve_launch_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    launch_input = kwargs["input"]

    analysis = Analysis.objects.filter_for_user(principal).get_subclass(
        id=launch_input["id"]
    )

    try:
        analysis.run_if_has_perm(
            principal,
            request=request,
            webhook_path=reverse("connector_accessmod:webhook"),
        )
        return {"success": True, "analysis": analysis, "errors": []}
    except ValueError:
        return {"success": False, "analysis": analysis, "errors": ["LAUNCH_FAILED"]}
    except PermissionDenied:
        return {"success": False, "analysis": analysis, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("deleteAccessmodAnalysis")
@transaction.atomic
def resolve_delete_accessmod_analysis(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        analysis = Analysis.objects.filter_for_user(principal).get_subclass(
            id=delete_input["id"]
        )
        analysis.delete_if_has_perm(principal)
        return {"success": True, "errors": []}
    except Analysis.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except ValueError:
        return {"success": False, "errors": ["DELETE_FAILED"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


accessmod_bindables = [
    accessmod_query,
    accessmod_mutations,
    project_object,
    project_order_by,
    owner_union,
    ownership_interface,
    permission_object,
    fileset_object,
    analysis_interface,
]
