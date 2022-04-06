import typing
from functools import cache
from importlib import import_module
from types import ModuleType

from django.apps import apps
from django.contrib.auth.backends import BaseBackend

from hexa.user_management import models as user_management_models


class PermissionsBackend(BaseBackend):
    """Custom permission backend that uses model methods to check for permissions."""

    @staticmethod
    @cache
    def _get_permission_function(perm: str) -> typing.Optional[ModuleType]:
        try:
            app_label, app_perm = perm.split(".")
        except ValueError:
            raise ValueError(
                f'Invalid permission "{perm}" (Should be "app_label.perm")'
            )

        try:
            app_config = apps.get_app_config(app_label)
            permissions_module = import_module(f"{app_config.name}.permissions")
        except LookupError:
            return None

        return getattr(permissions_module, app_perm)

    def has_perm(
        self,
        user_obj: user_management_models.User,
        perm: str,
        obj: typing.Any = None,
    ):
        permission_function = self._get_permission_function(perm)
        if permission_function is None:
            return False

        return permission_function(user_obj, obj)
