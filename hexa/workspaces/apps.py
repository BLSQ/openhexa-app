from hexa.app import CoreAppConfig


class WorkspacesConfig(CoreAppConfig):
    name = "hexa.workspaces"
    label = "workspaces"

    ANONYMOUS_URLS = ["workspaces:credentials"]
