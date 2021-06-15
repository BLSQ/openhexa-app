from ariadne import (
    QueryType,
    make_executable_schema,
    MutationType,
    ObjectType,
    snake_case_fallback_resolvers,
)
from django.contrib.auth import authenticate, login

from hexa.catalog.schema import catalog_type_defs, catalog

type_defs = """
    type Query {
        me: User
        catalog: Catalog!
    }
    type User {
        id: String!
        username: String!
    }
    type Mutation {
        login(username: String!, password: String!): User
    }
"""

query = QueryType()


@query.field("me")
def resolve_me(_, info):
    request = info.context["request"]

    return request.user if request.user.is_authenticated else None


mutation = MutationType()

user = ObjectType("User")


@query.field("catalog")
def resolve_catalog(*_):
    return {}


@mutation.field("login")
def resolve_login(_, info, username, password):
    request = info.context["request"]
    user_candidate = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user_candidate)

        return user_candidate
    else:
        return None


schema = make_executable_schema(
    [catalog_type_defs, type_defs],
    [query, catalog, mutation, user, snake_case_fallback_resolvers],
)
