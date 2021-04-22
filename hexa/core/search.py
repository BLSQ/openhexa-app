def locale_to_text_search_config(locale):
    """Converts an ISO-639(/ISO-3166) locale(/country) string to a PostgreSQL text search config string
    (SELECT cfgname FROM pg_ts_config;)
    """

    # TODO: more choices - and sync with PostgresSearchConfig
    if locale == "en" or locale[:3] == "en-":
        return "english"
    elif locale == "fr" or locale[:3] == "fr-":
        return "french"

    return "simple"
