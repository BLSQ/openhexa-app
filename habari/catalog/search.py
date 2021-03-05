from habari.catalog.connectors import get_connector_app_configs
from habari.catalog.models import Datasource


def perform_search(query, limit=10):
    tokens = query.split(" ")

    try:
        search_type = next(t for t in tokens if t[:5] == "type:")[5:]
        other_tokens = [t for t in tokens if t[:5] != "type:"]
        query = " ".join(other_tokens)
    except StopIteration:
        search_type = None

    results = Datasource.objects.search(query, limit=limit, search_type=search_type)

    connector_app_configs = get_connector_app_configs()
    for app_config in connector_app_configs:
        results += app_config.connector.objects.search(
            query, limit=limit, search_type=search_type
        )

    filtered_results = [result for result in results if result.rank > 0.01]

    return sorted(filtered_results, key=lambda r: r.rank, reverse=True)[:limit]
