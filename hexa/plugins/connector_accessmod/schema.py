from ariadne import QueryType
from django.http import HttpRequest
from django.utils import timezone
from django_countries.fields import Country

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

    if kwargs["id"] == "69fadc86-bfda-40a1-a7b2-de346a790277":
        return {
            "id": "69fadc86-bfda-40a1-a7b2-de346a790277",
            "name": "Sample project",
            "country": Country("BE"),
            "owner": request.user,
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        }

    return None


accessmod_bindables = [accessmod_query]
