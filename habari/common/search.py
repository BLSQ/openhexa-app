def locale_to_text_search_config(locale):
    # TODO: more choices - and sync with PostgresSearchConfig
    if locale == "en" or locale[:3] == "en-":
        return "english"
    elif locale == "fr" or locale[:3] == "fr-":
        return "french"

    return "simple"
