from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class UserManagementConfig(AppConfig, CoreAppConfig):
    name = "hexa.user_management"
    label = "user_management"

    verbose_name = "User management"
