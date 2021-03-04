from habari.catalog.connectors import get_connector_app_configs
from habari.catalog.models import Datasource


def perform_search(query, limit=10):
    results = Datasource.objects.search(query)

    connector_app_configs = get_connector_app_configs()
    for app_config in connector_app_configs:
        results += app_config.connector.objects.search(query)

    return sorted(results, key=lambda r: r.rank, reverse=True)[:limit]
