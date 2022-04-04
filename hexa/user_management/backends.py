import typing

from django.contrib.auth.backends import BaseBackend

from hexa.user_management import models as user_management_models


class PermissionsBackend(BaseBackend):
    """Custom permission backend that uses model methods to check for permissions."""

    def has_perm(
        self,
        user_obj: user_management_models.User,
        perm: typing.Callable[[user_management_models.User, typing.Any], bool],
        obj: typing.Any = None,
    ):
        return perm(user_obj, obj)
