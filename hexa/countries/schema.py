import pathlib

from ariadne import ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest

from .models import Country, WHOBoundary

countries_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

countries_query = QueryType()


@countries_query.field("country")
def resolve_country(_, info, **kwargs):
    # FIXME how to manage 404?
    code = kwargs.get("code")
    alpha3 = kwargs.get("alpha3")
    if code is not None:
        return Country.objects.get(code=code)
    elif alpha3 is not None:
        return Country.objects.get(alpha3=alpha3)
    else:
        raise ValueError("Please provide either code or alpha3")


@countries_query.field("countries")
def resolve_countries(_, info, **kwargs):
    return Country.objects.all().order_by("code")


@countries_query.field("boundaries")
def resolve_boundaries(_, info, **kwargs):
    country_code = kwargs.get("country_code")
    level = kwargs.get("level")
    return WHOBoundary.objects.filter(
        country__code=country_code, administrative_level=level
    ).order_by("name")


country_object = ObjectType("Country")


@country_object.field("flag")
def resolve_country_flag(obj: Country, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(obj.flag)


@country_object.field("whoInfo")
def resolve_country_who_info(obj: Country, info):
    return obj.get_who_info()


@country_object.field("alpha3")
def resolve_country_alpha3(obj: Country, info):
    # FIXME/ why is it necessary?
    return obj.alpha3


countries_bindables = [
    countries_query,
    country_object,
]
