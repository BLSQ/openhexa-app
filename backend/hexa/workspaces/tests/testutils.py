from unittest.mock import patch

from hexa.databases.api import load_database_sample_data
from hexa.databases.tests.helpers import provision_workspace_database
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import Workspace


def create_workspace(
    principal: User | None = None,
    *,
    name: str = "Test Workspace",
    organization: Organization | None = None,
    real_database=None,
    **kwargs,
) -> Workspace:
    """Create a Workspace (and, if needed, its Organization) for tests.

    Workspaces always belong to an organization, so tests that don't care about
    the organization can omit it and get a default one. Pass ``principal`` to go
    through ``create_if_has_perm``; omit it for a plain ``create``.

    ``create_if_has_perm`` provisions the workspace database, which is a CREATE
    DATABASE that no test rollback can undo, so that part is mocked out by
    default. Tests that actually query the workspace database pass
    ``real_database``: the TestCase class from ``setUpTestData``, or the instance
    from ``setUp`` or a test method. They then get a real database, dropped again
    on cleanup.
    """
    if organization is None:
        organization = Organization.objects.create(name=f"{name} Organization")
    if principal is None:
        return Workspace.objects.create(name=name, organization=organization, **kwargs)

    with (
        patch("hexa.workspaces.models.create_database"),
        patch("hexa.workspaces.models.load_database_sample_data"),
    ):
        workspace = Workspace.objects.create_if_has_perm(
            principal, name=name, organization=organization, **kwargs
        )

    if real_database is not None:
        provision_workspace_database(real_database, workspace)
        if kwargs.get("load_sample_data"):
            load_database_sample_data(workspace.db_name, workspace.db_password)

    return workspace
