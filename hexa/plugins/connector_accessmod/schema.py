from ariadne import QueryType
from django.http import HttpRequest

from hexa.plugins.connector_accessmod.models import Project

accessmod_type_defs = """
    # Projects
    type AccessmodProject {
        id: String!
        name: String!
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
        country: CountryInput!
    }
    type AccessmodProjectResult {
        success: Boolean!
        project: AccessmodProject
    }
    extend type Query {
        accessModProject(id: String): AccessmodProject
        accessModProjects: AccessmodProjectPage!
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
        return Project.objects.filter_for_user(request.user).get()
    except Project.DoesNotExist:
        return None


accessmod_bindables = [accessmod_query]
