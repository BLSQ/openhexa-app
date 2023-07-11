from functools import cache

import django.apps


@cache
def limit_data_source_types():
    from hexa.core.models.indexes import BaseIndexableMixin

    all_models = django.apps.apps.get_models()
    indexables = [x for x in all_models if issubclass(x, BaseIndexableMixin)]
    names = [x.__name__.lower() for x in indexables]
    return {"model__in": names}
