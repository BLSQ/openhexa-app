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
    def _get_permission_module(
        app_label: str,
    ) -> typing.Optional[ModuleType]:
        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            return None

        # Third-party apps (e.g. django_sql_dashboard) don't follow the OpenHEXA
        # permissions module convention, so this backend can't handle their permissions
        if not app_config.name.startswith("hexa."):
            return None

        return import_module(f"{app_config.name}.permissions")

    def has_perm(
        self,
        user_obj: user_management_models.User,
        perm: str,
        obj: typing.Any = None,
    ):
        try:
            app_label, app_perm = perm.split(".")
        except ValueError:
            return False  # No dot? Not an OpenHEXA permission, this backend can't handle it

        permission_module = self._get_permission_module(app_label)
        if permission_module is None:
            return False  # Not an OpenHEXA app, let other backends handle it

        try:
            permission_function = getattr(permission_module, app_perm)
        except AttributeError:
            raise AttributeError(
                f'The "{app_label}" app has no "{app_perm}" permission'
            )

        args = [user_obj]
        if obj is not None:
            args.append(obj)

        return permission_function(*args)
