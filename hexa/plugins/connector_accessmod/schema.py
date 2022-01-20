from ariadne import MutationType, QueryType
from django.http import HttpRequest
from django_countries.fields import Country

from hexa.core.graphql import result_page
from hexa.plugins.connector_accessmod.models import Project

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
    input UpdateAccessmodProjectInput {
        id: String!
        name: String
        spatialResolution: Int
        country: CountryInput
    }
    input DeleteAccessmodProjectInput {
        id: String!
    }
    type CreateAccessmodProjectResult {
        success: Boolean!
        project: AccessmodProject
    }
    type UpdateAccessmodProjectResult {
        success: Boolean!
        project: AccessmodProject
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


accessmod_bindables = [accessmod_query, accessmod_mutations]
