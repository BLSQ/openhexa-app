from ariadne import QueryType
from django.http import HttpRequest

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
    input AccessmodProjectInput {
        name: String!
        spatialResolution: Int!
        country: CountryInput!
    }
    type AccessmodProjectResult {
        success: Boolean!
        project: AccessmodProject
    }
    extend type Query {
        accessModProject(id: String): AccessmodProject
        accessModProjects(page: Int, perPage: Int): AccessmodProjectPage!
    }
    extend type Mutation {
        createAccessmodProject(input: AccessmodProjectInput): AccessmodProjectResult
        updatedAccessmodProject(id: String, input: AccessmodProjectInput): AccessmodProjectResult
    }
"""

accessmod_query = QueryType()


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


accessmod_bindables = [accessmod_query]
