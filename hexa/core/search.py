import typing
import uuid

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from hexa.core.search_utils import tokenize
from hexa.user_management.models import User


def get_search_options(user: User, query: str):
    from hexa.catalog.models import Datasource

    type_options, datasource_options = [], []
    for ct in ContentType.objects.filter(app_label__startswith="connector_"):
        model = ct.model_class()
        if not model:
            continue

        if issubclass(model, Datasource):
            for obj in model.objects.all():
                datasource_options.append(
                    {
                        "value": obj.id,
                        "label": f"({ct.app_label[10:].capitalize()}) {obj.display_name}",
                        "selected": f"datasource:{obj.id}" in query,
                    }
                )
        if hasattr(
            model, "searchable"
        ):  # TODO: remove (see comment in datasource_index command)
            content_code = f"{ct.app_label[10:]}_{ct.model}"
            type_options.append(
                {
                    "value": f"{content_code}",
                    "label": ct.name,
                    "selected": f"type:{content_code}" in query,
                }
            )

    if user.has_feature_flag("collections"):
        type_options.append(
            {
                "value": "collection",
                "label": _("Collection"),
                "selected": "type:collection" in query,
            }
        )
    type_options = sorted(type_options, key=lambda e: e["label"])
    datasource_options = sorted(datasource_options, key=lambda e: e["label"])

    return type_options, datasource_options


def search(user: User, query: str, size: int = 10) -> typing.List[dict]:
    from hexa.catalog.models import Index
    from hexa.data_collections.models import Collection

    if len(query) == 0:
        return []

    results = []
    tokens = tokenize(query, ["type", "datasource"])
    # Filters
    types = [t.value[5:] for t in tokens if t.value.startswith("type:")]
    datasources = []
    for t in tokens:
        if t.value.startswith("datasource:"):
            try:
                datasources.append(uuid.UUID(t.value[11:]))
            except ValueError:
                continue

    # As of now we do not index collections so we also search for collections matching the criteria and
    # merge the results with the index results.
    if not (len(types) == 1 and types[0] == "collection"):
        # Do not search in indexes if what the user wants to see is only collections
        results = list(
            Index.objects.filter_for_user(user).filter_for_tokens(tokens)
            # filter by resources type
            .filter_for_types(types)
            # filter by datasources
            .filter_for_datasources(datasources)
            # exclude s3keep, artifact of s3content mngt
            .exclude(external_name=".s3keep")[:size]
        )

    # Search for collections if it's enabled and user wants to search in all types or only for collections
    if user.has_feature_flag("collections") and (
        len(types) == 0 or "collection" in types
    ):
        results += list(Collection.objects.filter_for_user(user).search(query)[:size])
        results.sort(key=lambda x: getattr(x, "rank"), reverse=True)
        results = results[:size]

    return results
