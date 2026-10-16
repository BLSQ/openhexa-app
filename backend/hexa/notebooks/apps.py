from hexa.app import CoreAppConfig


class NotebooksConfig(CoreAppConfig):
    name = "hexa.notebooks"
    label = "notebooks"

    ANONYMOUS_URLS = [
        "notebooks:credentials",
    ]
