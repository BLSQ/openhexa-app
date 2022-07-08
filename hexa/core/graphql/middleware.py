from ariadne.contrib.federation.utils import includes_directive
from ariadne.contrib.tracing.utils import is_introspection_field
from graphql import GraphQLError


def authentication_middleware(resolver, obj, info, **args):
    if (
        is_introspection_field(info)
        or info.context["request"].user.is_authenticated
        or includes_directive(info, "authNotRequired")
    ):
        return resolver(obj, info, **args)

    raise GraphQLError("This operation is not allowed.")
