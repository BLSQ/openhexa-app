def authentication_middleware(resolver, obj, info, **args):
    if (
        info.field_name != "schema"
        and not info.context["request"].user.is_authenticated
    ):
        return None
    return resolver(obj, info, **args)
