import uuid
from mimetypes import guess_extension

from ariadne import MutationType, QueryType
from django.http import HttpRequest
from django_countries.fields import Country

from config import settings
from hexa.core.graphql import result_page
from hexa.plugins.connector_accessmod.models import File, Fileset, FilesetRole, Project
from hexa.plugins.connector_s3.api import generate_upload_url
from hexa.plugins.connector_s3.models import Bucket

accessmod_type_defs = """
    # Projects
    type AccessmodProject {
        id: String!
        name: String!
        spatialResolution: Int!
        country: Country!
        owner: User!
        createdAt: DateTime!
        updatedAt: DateTime!
    }
    type AccessmodProjectPage {
        pageNumber: Int!
        totalPages: Int!
        totalItems: Int!
        items: [AccessmodProject!]!
    }
    input CreateAccessmodProjectInput {
        name: String!
        spatialResolution: Int!
        country: CountryInput!
    }
    type CreateAccessmodProjectResult {
        success: Boolean!
        project: AccessmodProject
    }
    input UpdateAccessmodProjectInput {
        id: String!
        name: String
        spatialResolution: Int
        country: CountryInput
    }
    type UpdateAccessmodProjectResult {
        success: Boolean!
        project: AccessmodProject
    }
    input DeleteAccessmodProjectInput {
        id: String!
    }
    type DeleteAccessmodProjectResult {
        success: Boolean!
    }
    extend type Query {
        accessModProject(id: String): AccessmodProject
        accessModProjects(page: Int, perPage: Int): AccessmodProjectPage!
    }
    extend type Mutation {
        createAccessmodProject(input: CreateAccessmodProjectInput): CreateAccessmodProjectResult
        updateAccessmodProject(input: UpdateAccessmodProjectInput): UpdateAccessmodProjectResult
        deleteAccessmodProject(input: DeleteAccessmodProjectInput): DeleteAccessmodProjectResult
    }
    
    # Filesets
    type AccessmodFileset {
        id: String!
        name: String!
        role: AccessmodFilesetRole
        owner: User!
        createdAt: DateTime!
        updatedAt: DateTime!
    }
    type AccessmodFilesetPage {
        pageNumber: Int!
        totalPages: Int!
        totalItems: Int!
        items: [AccessmodFileset!]!
    }
    type AccessmodFilesetRole {
        id: String!
        name: String!
        format: AccessmodFilesetFormat!
        createdAt: DateTime!
        updatedAt: DateTime!
    }
    enum AccessmodFilesetFormat {
        VECTOR
        RASTER
        TABULAR
    }
    type AccessModFile {
        id: String!
        uri: String!
        fileset: AccessmodFileset
        mimeType: String!
        createdAt: DateTime!
        updatedAt: DateTime!
    }
    input CreateAccessmodFilesetInput {
        name: String!
        projectId: String!
        roleId: String!
    }
    type CreateAccessmodFilesetResult {
        success: Boolean!
        fileset: AccessmodFileset
    }
    input PrepareAccessModFileUploadInput {
        projectId: String!
        mimeType: String!
    }
    type PrepareAccessModFileUploadResult {
        success: Boolean!
        uploadUrl: String
        fileUri: String
    }
    input CreateAccessModFileInput {
        filesetId: String!
        uri: String!
        mimeType: String!
    }
    type CreateAccessModFileResult {
        success: Boolean!
        file: AccessModFile
    }
    extend type Mutation {
        createAccessmodFileset(input: CreateAccessmodFilesetInput): CreateAccessmodFilesetResult
        prepareAccessModFileUpload(input: PrepareAccessModFileUploadInput): PrepareAccessModFileUploadResult
        createAccessModFile(input: CreateAccessModFileInput): CreateAccessModFileResult
    }
"""

accessmod_query = QueryType()
accessmod_mutations = MutationType()


@accessmod_query.field("accessModProject")
def resolve_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Project.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Project.DoesNotExist:
        return None


@accessmod_query.field("accessModProjects")
def resolve_accessmod_projects(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = Project.objects.filter_for_user(request.user)

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("page")
    )


@accessmod_mutations.field("createAccessmodProject")
def resolve_create_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    project = Project.objects.create(
        owner=request.user,
        name=create_input["name"],
        country=Country(create_input["country"]["code"]),
        spatial_resolution=create_input["spatialResolution"],
    )

    return {"success": True, "project": project}


@accessmod_mutations.field("updateAccessmodProject")
def resolve_update_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(request.user).get(
            id=update_input["id"]
        )
        # TODO: rationalize
        changed = False
        if "name" in update_input:
            project.name = update_input["name"]
            changed = True
        if "spatialResolution" in update_input:
            project.spatial_resolution = update_input["spatialResolution"]
            changed = True
        if "country" in update_input:
            project.country = Country(update_input["country"]["code"])
            changed = True
        if changed:
            project.save()

        return {"success": True, "project": project}
    except Project.DoesNotExist:
        return {"success": False}


@accessmod_mutations.field("deleteAccessmodProject")
def resolve_delete_accessmod_project(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    update_input = kwargs["input"]

    try:
        project = Project.objects.filter_for_user(request.user).get(
            id=update_input["id"]
        )
        project.delete()  # TODO: soft-delete?

        return {"success": True}
    except Project.DoesNotExist:
        return {"success": False}


@accessmod_mutations.field("createAccessmodFileset")
def resolve_create_accessmod_fileset(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    fileset = Fileset.objects.create(
        owner=request.user,
        name=create_input["name"],
        project=Project.objects.filter_for_user(request.user).get(
            id=create_input["projectId"]
        ),
        role=FilesetRole.objects.get(id=create_input["roleId"]),
    )

    return {"success": True, "fileset": fileset}


@accessmod_mutations.field("prepareAccessModFileUpload")
def resolve_prepare_accessmod_file_upload(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    prepare_input = kwargs["input"]
    project = Project.objects.filter_for_user(request.user).get(
        id=prepare_input["projectId"]
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

    target_key = (
        f"{project.id}/{uuid.uuid4()}{guess_extension(prepare_input['mimeType'])}"
    )
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


@accessmod_mutations.field("createAccessModFile")
def resolve_create_accessmod_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    create_input = kwargs["input"]
    file = File.objects.create(
        uri=create_input["uri"],
        mime_type=create_input["mimeType"],
        fileset=Fileset.objects.filter_for_user(request.user).get(
            id=create_input["filesetId"]
        ),
    )

    return {"success": True, "file": file}


accessmod_bindables = [accessmod_query, accessmod_mutations]
