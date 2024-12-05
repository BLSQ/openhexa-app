import logging
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
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.urls import reverse
from slugify import slugify
from stringcase import snakecase

import hexa.plugins.connector_s3.api as s3_api
from hexa.core import mimetypes
from hexa.core.graphql import result_page
from hexa.countries.models import Country
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AccessRequest,
    Analysis,
    File,
    Fileset,
    FilesetRole,
    GeographicCoverageAnalysis,
    Project,
    ProjectPermission,
    ZonalStatisticsAnalysis,
)
from hexa.plugins.connector_accessmod.queue import validate_fileset_queue
from hexa.plugins.connector_accessmod.utils import send_mail_to_accessmod_superusers
from hexa.plugins.connector_s3.models import Bucket as S3Bucket
from hexa.user_management.models import Team, User
from hexa.user_management.schema import me_permissions_object

logger = logging.getLogger(__name__)

accessmod_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
accessmod_query = QueryType()
accessmod_mutations = MutationType()


@me_permissions_object.field("createAccessmodProject")
def resolve_me_permissions_create_project(me, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.create_project")


@me_permissions_object.field("manageAccessmodAccessRequests")
def resolve_me_permissions_manage_access_requests(me, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.manage_access_requests")


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


@project_object.field("members")
def resolve_accessmod_project_members(project: Project, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    return project.projectpermission_set.filter_for_user(principal).all()


@project_object.field("permissions")
def resolve_accessmod_project_permissions(project: Project, info):
    return project


project_permissions_object = ObjectType("AccessmodProjectPermissions")


@project_permissions_object.field("update")
def resolve_accessmod_project_permissions_update(project: Project, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.update_project", project)


@project_permissions_object.field("createPermission")
def resolve_accessmod_project_permissions_create_permission(project: Project, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm(
        "connector_accessmod.create_project_permission", [project, request.user, None]
    )


@project_permissions_object.field("delete")
def resolve_accessmod_project_permissions_delete(project: Project, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.delete_project", project)


@project_permissions_object.field("createFileset")
def resolve_accessmod_project_permissions_create_fileset(project: Project, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.create_fileset", project)


@project_permissions_object.field("createAnalysis")
def resolve_accessmod_project_permissions_create_analysis(project: Project, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.create_analysis", project)


@project_permissions_object.field("createMember")
def resolve_accessmod_project_permissions_create_member(project: Project, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.create_member", project)


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

    order_by = kwargs.get("order_by", None)
    if order_by is not None:
        queryset = queryset.order_by(order_by)

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@accessmod_mutations.field("createAccessmodProject")
@transaction.atomic
def resolve_create_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    country = Country.objects.get(code=create_input["country"]["code"])
    if "extent" in create_input:
        extent = create_input["extent"]
    else:
        extent = country.simplified_extent.tuple[0]

    try:
        project = Project.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
            country=country.code,
            spatial_resolution=create_input["spatial_resolution"],
            crs=create_input["crs"],
            description=create_input.get("description", ""),
            extent=extent,
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
        for scalar_field in ["name", "description"]:
            if scalar_field in update_input:
                changes[snakecase(scalar_field)] = update_input[scalar_field]

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


project_member_object = ObjectType("AccessmodProjectMember")

fileset_permissions_object = ObjectType("AccessmodFilesetPermissions")


@fileset_permissions_object.field("update")
def resolve_fileset_permission_update(fileset: Fileset, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.update_fileset", fileset)


@fileset_permissions_object.field("delete")
def resolve_fileset_permission_delete(fileset: Fileset, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.delete_fileset", fileset)


@fileset_permissions_object.field("createFile")
def resolve_fileset_permission_create_file(fileset: Fileset, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("connector_accessmod.create_file", fileset)


@accessmod_mutations.field("createAccessmodProjectMember")
@transaction.atomic
def resolve_create_accessmod_project_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        user = (
            User.objects.get(id=create_input["user_id"])
            if "userId" in create_input
            else None
        )
        team = (
            Team.objects.get(id=create_input["team_id"])
            if "team_id" in create_input
            else None
        )
        project = Project.objects.get(pk=create_input["project_id"])
        member = ProjectPermission.objects.create_if_has_perm(
            principal,
            project=project,
            user=user,
            team=team,
            mode=create_input["mode"],
        )

        return {"success": True, "member": member, "errors": []}
    except NotImplementedError:
        return {"success": False, "errors": ["NOT_IMPLEMENTED"]}
    except (Team.DoesNotExist, User.DoesNotExist, Project.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("updateAccessmodProjectMember")
@transaction.atomic
def resolve_update_accessmod_project_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        member = ProjectPermission.objects.filter_for_user(user=principal).get(
            id=update_input["id"]
        )
        member.update_if_has_perm(principal, mode=update_input["mode"])

        return {"success": True, "member": member, "errors": []}
    except NotImplementedError:
        return {"success": False, "errors": ["NOT_IMPLEMENTED"]}
    except ProjectPermission.DoesNotExist:
        return {"success": False, "member": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "member": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("deleteAccessmodProjectMember")
@transaction.atomic
def resolve_delete_accessmod_project_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        permission = ProjectPermission.objects.filter_for_user(user=principal).get(
            id=delete_input["id"]
        )
        permission.delete_if_has_perm(principal)

        return {"success": True, "errors": []}
    except NotImplementedError:
        return {"success": False, "errors": ["NOT_IMPLEMENTED"]}
    except ProjectPermission.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


# Filesets
fileset_object = ObjectType("AccessmodFileset")


@fileset_object.field("files")
def resolve_accessmod_fileset_files(fileset: Fileset, info, **kwargs):
    return [f for f in fileset.file_set.all()]


@fileset_object.field("permissions")
def resolve_accessmod_fileset_permissions(fileset: Fileset, info, **kwargs):
    return fileset


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
        .filter(project_id=kwargs["project_id"])
        .order_by("-created_at")
    )
    if "role_id" in kwargs:
        queryset = queryset.filter(role__id=kwargs["role_id"])
    if "term" in kwargs:
        queryset = queryset.filter(name__icontains=kwargs["term"])
    if "mode" in kwargs:
        queryset = queryset.filter(mode=kwargs["mode"])

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@accessmod_mutations.field("createAccessmodFileset")
@transaction.atomic
def resolve_create_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        kwargs = {
            "name": create_input["name"],
            "role": FilesetRole.objects.get(id=create_input["role_id"]),
            "metadata": create_input.get("metadata", {}),
        }
        fileset = Fileset.objects.create_if_has_perm(
            principal,
            project=Project.objects.filter_for_user(request.user).get(
                id=create_input["project_id"]
            ),
            automatic_acquisition=create_input.get("automatic", False),
            **kwargs,
        )
        return {"success": True, "fileset": fileset, "errors": []}
    except IntegrityError:
        return {"success": False, "fileset": None, "errors": ["NAME_DUPLICATE"]}
    except PermissionDenied:
        return {"success": False, "fileset": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("updateAccessmodFileset")
@transaction.atomic
def resolve_update_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        fileset = Fileset.objects.filter_for_user(principal).get(
            id=update_input.pop("id")
        )
        changes = {}

        for scalar_field in [
            "name",
            "metadata",
        ]:
            try:
                scalar_value = update_input.pop(scalar_field)
                changes[snakecase(scalar_field)] = scalar_value
            except KeyError:
                pass

        if len(changes) > 0:
            try:
                fileset.update_if_has_perm(principal, **changes)
            except IntegrityError:
                return {
                    "success": False,
                    "fileset": fileset,
                    "errors": ["NAME_DUPLICATE"],
                }
            except PermissionDenied:
                return {
                    "success": False,
                    "fileset": fileset,
                    "errors": ["PERMISSION_DENIED"],
                }

        return {"success": True, "fileset": fileset, "errors": []}
    except Fileset.DoesNotExist:
        return {"success": False, "fileset": None, "errors": ["NOT_FOUND"]}


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
    except IntegrityError:
        return {"success": False, "errors": ["FILESET_IN_USE"]}
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
        id=prepare_input["fileset_id"]
    )

    # This is a temporary solution until we figure out storage requirements
    if settings.ACCESSMOD_BUCKET_NAME is None:
        raise ValueError("ACCESSMOD_BUCKET_NAME is not set")

    uri_protocol, bucket_name = settings.ACCESSMOD_BUCKET_NAME.split("://")
    bucket_name = bucket_name.rstrip("/")
    if uri_protocol == "s3":
        Bucket = S3Bucket
    else:
        raise ValueError(f"Protocol {uri_protocol} not supported.")

    try:
        bucket = Bucket.objects.get(name=bucket_name)
    except Bucket.DoesNotExist:
        raise ValueError(f"The {settings.ACCESSMOD_BUCKET_NAME} bucket does not exist")
    target_slug = slugify(fileset.name, separator="_")
    target_key = f"{fileset.project.id}/{target_slug}{mimetypes.guess_extension(prepare_input['mime_type'])}"

    if uri_protocol == "s3":
        upload_url = s3_api.generate_upload_url(
            bucket=bucket,
            target_key=target_key,
        )
    else:
        raise ValueError(f"Protocol {uri_protocol} not supported.")

    return {
        "success": True,
        "upload_url": upload_url,
        "file_uri": f"{uri_protocol}://{bucket.name}/{target_key}",
    }


@accessmod_mutations.field("prepareAccessmodFileDownload")
@transaction.atomic
def resolve_prepare_accessmod_file_download(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    prepare_input = kwargs["input"]
    file = File.objects.filter_for_user(principal).get(id=prepare_input["file_id"])

    # This is a temporary solution until we figure out storage requirements
    if settings.ACCESSMOD_BUCKET_NAME is None:
        raise ValueError("ACCESSMOD_BUCKET_NAME is not set")

    uri_protocol, bucket_name = settings.ACCESSMOD_BUCKET_NAME.split("://")
    bucket_name = bucket_name.rstrip("/")
    if uri_protocol == "s3":
        Bucket = S3Bucket
    else:
        raise ValueError(f"Protocol {uri_protocol} not supported.")

    try:
        bucket = Bucket.objects.get(name=bucket_name)
    except Bucket.DoesNotExist:
        raise ValueError(f"The {settings.ACCESSMOD_BUCKET_NAME} bucket does not exist")

    if uri_protocol == "s3":
        download_url = s3_api.generate_download_url(
            bucket=bucket,
            # Ugly workaround, TBD when we know more about storage
            target_key=file.uri.replace(f"s3://{bucket.name}/", ""),
        )
    else:
        raise ValueError(f"Protocol {uri_protocol} not supported.")

    return {
        "success": True,
        "download_url": download_url,
    }


@accessmod_mutations.field("prepareAccessmodFilesetVisualizationDownload")
@transaction.atomic
def resolve_prepare_accessmod_fileset_visualization_download(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    prepare_input = kwargs["input"]
    try:
        fileset: Fileset = Fileset.objects.filter_for_user(principal).get(
            id=prepare_input["id"]
        )
    except Fileset.DoesNotExist:
        return {"success": False}

    if not fileset.visualization_uri:
        return {"success": False}
    uri = fileset.visualization_uri

    # TODO This is a temporary solution until we figure out storage requirements
    if settings.ACCESSMOD_BUCKET_NAME is None:
        raise ValueError("ACCESSMOD_BUCKET_NAME is not set")

    uri_protocol, bucket_name = settings.ACCESSMOD_BUCKET_NAME.split("://")
    bucket_name = bucket_name.rstrip("/")
    if uri_protocol == "s3":
        Bucket = S3Bucket
    try:
        bucket = Bucket.objects.get(name=bucket_name)
    except Bucket.DoesNotExist:
        raise ValueError(f"The {settings.ACCESSMOD_BUCKET_NAME} bucket does not exist")

    try:
        if uri_protocol == "s3":
            download_url = s3_api.generate_download_url(
                bucket=bucket,
                # Ugly workaround, TBD when we know more about storage
                target_key=uri.replace(f"s3://{bucket.name}/", ""),
            )
        else:
            raise ValueError(f"Protocol {uri_protocol} not supported.")

    except Exception as err:
        logger.exception(err)
        return {"success": False}

    return {
        "success": True,
        "url": download_url,
    }


@accessmod_mutations.field("createAccessmodFile")
@transaction.atomic
def resolve_create_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    fileset = Fileset.objects.filter_for_user(principal).get(
        id=create_input["fileset_id"]
    )
    try:
        file = File.objects.create_if_has_perm(
            principal,
            uri=create_input["uri"],
            mime_type=create_input["mime_type"],
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


@accessmod_query.field("accessmodFilesetRole")
def resolve_accessmod_fileset_role(_, info, **kwargs):
    try:
        return FilesetRole.objects.get(id=kwargs["id"])
    except FilesetRole.DoesNotExist:
        return None


@accessmod_query.field("accessmodFilesetRoles")
def resolve_accessmod_fileset_roles(_, info, **kwargs):
    return FilesetRole.objects.all()


# Analysis
analysis_interface = InterfaceType("AccessmodAnalysis")


@analysis_interface.type_resolver
def resolve_analysis_type(analysis: Analysis, *_):
    if isinstance(analysis, AccessibilityAnalysis):
        return "AccessmodAccessibilityAnalysis"
    elif isinstance(analysis, GeographicCoverageAnalysis):
        return "AccessmodGeographicCoverageAnalysis"
    elif isinstance(analysis, ZonalStatisticsAnalysis):
        return "AccessmodZonalStatistics"

    return None


@analysis_interface.field("permissions")
def resolve_analysis_permissions(analysis: Analysis, info, **kwargs):
    return analysis


analysis_permissions = ObjectType("AccessmodAnalysisPermissions")


@analysis_permissions.field("update")
def resolve_analysis_permissions_update(analysis: Analysis, info):
    request: HttpRequest = info.context["request"]

    return request.user.has_perm("connector_accessmod.update_analysis", analysis)


@analysis_permissions.field("delete")
def resolve_analysis_permissions_delete(analysis: Analysis, info):
    request: HttpRequest = info.context["request"]

    return request.user.has_perm("connector_accessmod.delete_analysis", analysis)


@analysis_permissions.field("run")
def resolve_analysis_permissions_run(analysis: Analysis, info):
    request: HttpRequest = info.context["request"]

    return request.user.has_perm("connector_accessmod.run_analysis", analysis)


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
        .filter(project_id=kwargs["project_id"])
        .order_by("-created_at")
        .select_subclasses()
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
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
                id=create_input["project_id"]
            ),
            name=create_input["name"],
        )
        return {"success": True, "analysis": analysis, "errors": []}
    except IntegrityError:
        return {"success": False, "analysis": None, "errors": ["NAME_DUPLICATE"]}
    except PermissionDenied:
        return {"success": False, "analysis": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("createAccessmodZonalStatistics")
@transaction.atomic
def resolve_create_accessmod_zonal_statistics(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        analysis = ZonalStatisticsAnalysis.objects.create_if_has_perm(
            principal,
            project=Project.objects.filter_for_user(request.user).get(
                id=create_input["project_id"]
            ),
            name=create_input["name"],
        )
        return {"success": True, "analysis": analysis, "errors": []}
    except IntegrityError:
        return {"success": False, "analysis": None, "errors": ["NAME_DUPLICATE"]}
    except PermissionDenied:
        return {"success": False, "analysis": None, "errors": ["PERMISSION_DENIED"]}


@accessmod_mutations.field("updateAccessmodAccessibilityAnalysis")
@accessmod_mutations.field("updateAccessmodZonalStatistics")
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
            "invert_direction",
            "max_travel_time",
            "moving_speeds",
            "water_all_touched",
            "algorithm",
            "knight_move",
            "stack_priorities",
            "time_thresholds",
        ]:
            if scalar_field in update_input:
                changes[scalar_field] = update_input[scalar_field]

        for fileset_field in [
            "land_cover_id",
            "dem_id",
            "stack_id",
            "transport_network_id",
            "water_id",
            "barrier_id",
            "health_facilities_id",
            "population_id",
            "travel_times_id",
            "boundaries_id",
        ]:
            if fileset_field in update_input:
                fileset = (
                    Fileset.objects.filter_for_user(principal).get(
                        id=update_input[fileset_field]
                    )
                    if update_input[fileset_field] is not None
                    else None
                )

                changes[fileset_field] = fileset.id if fileset else None
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


@accessmod_query.field("accessmodAccessRequests")
def resolve_accessmod_access_requests(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    queryset = AccessRequest.objects.filter_for_user(request.user).order_by(
        "-created_at"
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@accessmod_mutations.field("requestAccessmodAccess")
@transaction.atomic
def resolve_request_accessmod_access(_, info, **kwargs):
    request = info.context["request"]
    request_input = kwargs["input"]

    try:
        access_request = AccessRequest.objects.create_if_has_perm(
            request.user,
            first_name=request_input["first_name"],
            last_name=request_input["last_name"],
            email=request_input["email"],
            accepted_tos=request_input["accept_tos"],
        )
    except (ValidationError, PermissionDenied):
        return {"success": False, "errors": ["INVALID"]}

    send_mail_to_accessmod_superusers(
        title=f"AcccessMod : {access_request.display_name} has requested an access to AccessMod.",
        template_name="connector_accessmod/mails/request_access",
        template_variables={
            "access_request": access_request,
            "manage_url": settings.ACCESSMOD_MANAGE_REQUESTS_URL,
        },
    )

    return {"success": True, "errors": []}


@accessmod_mutations.field("approveAccessmodAccessRequest")
@transaction.atomic
def resolve_approve_accessmod_access_request(_, info, **kwargs):
    request = info.context["request"]
    approve_input = kwargs["input"]

    try:
        access_request = AccessRequest.objects.filter_for_user(request.user).get(
            id=approve_input["id"]
        )
        access_request.approve_if_has_perm(request.user, request=request)
    except (AccessRequest.DoesNotExist, PermissionDenied, ValidationError):
        return {"success": False, "errors": ["INVALID"]}

    return {"success": True, "errors": []}


@accessmod_mutations.field("denyAccessmodAccessRequest")
@transaction.atomic
def resolve_deny_accessmod_access_request(_, info, **kwargs):
    request = info.context["request"]
    deny_input = kwargs["input"]

    try:
        access_request = AccessRequest.objects.filter_for_user(request.user).get(
            id=deny_input["id"]
        )
        access_request.deny_if_has_perm(request.user)
    except (AccessRequest.DoesNotExist, PermissionDenied, ValidationError):
        return {"success": False, "errors": ["INVALID"]}

    return {"success": True, "errors": []}


accessmod_bindables = [
    accessmod_query,
    accessmod_mutations,
    project_object,
    project_order_by,
    owner_union,
    ownership_interface,
    project_member_object,
    fileset_object,
    analysis_interface,
    analysis_permissions,
    project_permissions_object,
    fileset_permissions_object,
]
