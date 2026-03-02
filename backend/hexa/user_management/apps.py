from hexa.app import CoreAppConfig


class UserManagementConfig(CoreAppConfig):
    name = "hexa.user_management"
    label = "user_management"

    verbose_name = "User management"

    ANONYMOUS_URLS = [
        "logout",
        "password_reset",
        "password_reset_confirm",
        "password_reset_done",
        "password_reset_complete",
    ]
