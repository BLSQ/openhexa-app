import typing

from hexa.countries.models import Country
from hexa.files.api import create_bucket
from hexa.user_management.models import User

from .models import Workspace


def create_workspace(
    principal: User,
    name: str,
    description: str = None,
    countries: typing.Sequence[Country] = None,
):
    workspace = Workspace.objects.create_if_has_perm(
        principal, name, description=description, countries=countries
    )
    bucket = create_bucket(workspace)
    workspace.bucket_name = bucket.name
    workspace.save()

    return workspace
