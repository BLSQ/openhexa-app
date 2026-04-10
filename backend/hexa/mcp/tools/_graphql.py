from pathlib import Path

from django.conf import settings
from django.test import RequestFactory
from graphql import graphql_sync

from config.schema import schema

_GRAPHQL_DIR = Path(__file__).parent.parent / "graphql"
_QUERIES = "\n".join(f.read_text() for f in sorted(_GRAPHQL_DIR.glob("*.graphql")))


def _make_request(user):
    request = RequestFactory().get("/", SERVER_NAME=settings.BASE_HOSTNAME)
    request.user = user
    request.bypass_two_factor = True
    return request


def execute_graphql(user, operation_name, variables=None):
    result = graphql_sync(
        schema,
        _QUERIES,
        context_value={"request": _make_request(user)},
        variable_values=variables or {},
        operation_name=operation_name,
    )
    if result.errors:
        return {"errors": [str(e) for e in result.errors]}
    return result.data
