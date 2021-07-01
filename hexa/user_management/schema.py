from ariadne import ObjectType, MutationType, QueryType
from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django_countries import countries
from django_countries.fields import Country

from hexa.user_management.models import Organization

identity_type_defs = """
    extend type Query {
        me: User
        countries: [Country!]
    }
    type User {
        id: String!
        username: String!
    }
    type Organization {
        id: String!
        name: String!
        type: String!
        url: String!
        contactInfo: String!
    }
    type Country {
        code: String!
        alpha3: String!
        name: String!
        flag: String!
    }
    extend type Mutation {
        identityCheck(username: String!, password: String!): User
    }
"""

identity_query = QueryType()
identity_mutations = MutationType()


@identity_query.field("me")
def resolve_me(_, info):
    request = info.context["request"]

    return request.user if request.user.is_authenticated else None


@identity_query.field("countries")
def resolve_countries(*_):
    return [Country(c) for c, _ in countries]


@identity_mutations.field("identityCheck")
def resolve_login(_, info, username, password):
    request: HttpRequest = info.context["request"]
    user_candidate = authenticate(request, username=username, password=password)

    if user_candidate is not None:
        login(request, user_candidate)

        return user_candidate
    else:
        return None


country = ObjectType("Country")


@country.field("alpha3")
def resolve_alpha3(obj: Country, *_):
    return obj.alpha3


@country.field("flag")
def resolve_flag(obj: Country, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(obj.flag)


organization = ObjectType("Organization")


@organization.field("type")
def resolve_type(obj: Organization, *_):
    return obj.get_organization_type_display()


identity_bindables = [
    identity_query,
    country,
    organization,
    identity_mutations,
]
