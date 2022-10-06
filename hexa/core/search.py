import typing
import uuid

from django.utils.translation import gettext_lazy as _

from hexa.core.search_utils import tokenize
from hexa.user_management.models import User


def get_search_options(user: User, query: str):
    from hexa.catalog.models import Index

    type_options, datasource_options = [], []

    datasource_indexes = (
        Index.objects.filter_for_user(user).roots().select_related("content_type")
    )
    for source in datasource_indexes:
        datasource_options.append(
            {
                "value": source.object.id,
                "label": f"({source.app_label[10:].capitalize()}) {source.object.display_name}",
                "selected": f"datasource:{source.object.id}" in query
                if query
                else False,
            }
        )

    content_types = [
        x.content_type
        for x in Index.objects.filter_for_user(user)
        .filter_for_datasources([d.object.id for d in datasource_indexes])
        .order_by("content_type")
        .distinct("content_type")
        .select_related("content_type")
    ]
    for content_type in content_types:
        content_code = f"{content_type.app_label[10:]}_{content_type.model}"
        type_options.append(
            {
                "value": f"{content_code}",
                "label": content_type.name,
                "selected": f"type:{content_code}" in query if query else False,
            }
        )

    if user.has_feature_flag("collections"):
        type_options.append(
            {
                "value": "collection",
                "label": _("Collection"),
                "selected": "type:collection" in query if query else False,
            }
        )
    type_options = sorted(type_options, key=lambda e: e["label"])
    datasource_options = sorted(datasource_options, key=lambda e: e["label"])

    return type_options, datasource_options


def search(
    user: User,
    query: str,
    types=None,
    datasource_ids=None,
    page: int = 1,
    size: int = 10,
) -> typing.List[dict]:
    from hexa.catalog.models import Index
    from hexa.data_collections.models import Collection

    if len(query) == 0:
        return []

    results = []
    tokens = tokenize(query, ["type", "datasource"])
    # Filters
    if types is None:
        # Get types from the query tokens "type:my_model"
        types = [t.value[5:] for t in tokens if t.value.startswith("type:")]

    if datasource_ids is None:
        datasource_ids = []
        # Get datasources from the query tokens "datasource:<uuid>"
        for t in tokens:
            if t.value.startswith("datasource:"):
                try:
                    datasource_ids.append(uuid.UUID(t.value[11:]))
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
            .filter_for_datasources(datasource_ids)
            # exclude s3keep, artifact of s3content mngt
            .exclude(external_name=".s3keep")[: size * page]
        )

    # Search for collections if it's enabled and user wants to search in all types or only for collections
    if (
        user.has_feature_flag("collections")
        and (len(types) == 0 or "collection" in types)
        and len(datasource_ids) == 0
    ):
        results += list(Collection.objects.filter_for_user(user).search(query)[:size])
        results.sort(key=lambda x: getattr(x, "rank", None), reverse=True)

    # Slice the results to get only results from the page
    return results[page - 1 * size : size * page]
