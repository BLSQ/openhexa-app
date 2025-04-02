import typing
import uuid

from hexa.core.search_utils import tokenize
from hexa.user_management.models import User


def search(
    user: User,
    query: str,
    types=None,
    datasource_ids=None,
    page: int = 1,
    size: int = 10,
) -> typing.List[dict]:
    from hexa.catalog.models import Index

    if len(query) == 0:
        return []

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

    results = list(
        Index.objects.filter_for_user(user)
        .filter_for_tokens(tokens)
        # filter by resources type
        .filter_for_types(types)
        # filter by datasources
        .filter_for_datasources(datasource_ids)
        # exclude s3keep, artifact of s3content mngt
        .exclude(external_name=".s3keep")[: size * page]
    )

    # Slice the results to get only results from the page
    return results[page - 1 * size : size * page]
