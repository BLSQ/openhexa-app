from django.db import models


def locale_to_text_search_config(locale_string):
    """Converts an ISO-639(/ISO-3166) locale(/country) string to a PostgreSQL text search config string
    (SELECT cfgname FROM pg_ts_config;)
    """
    # TODO: more choices - and sync with PostgresSearchConfig
    if locale_string == "en" or locale_string[:3] == "en-":
        return "english"
    elif locale_string == "fr" or locale_string[:3] == "fr-":
        return "french"

    return "simple"


class PostgresTextSearchConfigField(models.CharField):
    """Custom field to store Postgres text search config values (see pg_ts_config)."""

    description = "A Postgres text search config value"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 100
        # TODO: more choices
        kwargs["choices"] = [
            ("simple", "simple"),
            ("french", "french"),
            ("english", "english"),
        ]
        kwargs["default"] = "simple"
        super().__init__(*args, **kwargs)
