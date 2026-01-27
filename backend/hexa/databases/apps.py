from hexa.app import CoreAppConfig


class DatabasesConfig(CoreAppConfig):
    name = "hexa.databases"
    label = "databases"

    # API endpoints that don't require session authentication (they use token auth)
    ANONYMOUS_URLS = [
        "databases:table_data_api",
        "databases:dataset_recipe_create",
        "databases:dataset_recipe_execute",
    ]
