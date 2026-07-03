from hexa.app import CoreAppConfig


class GitConfig(CoreAppConfig):
    name = "hexa.git"
    label = "git"
    ANONYMOUS_URLS = ["git:authorize", "forgejo_oauth_token"]
