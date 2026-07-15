from hexa.user_management.models import Organization, User
from hexa.workspaces.models import Workspace


def create_workspace(
    principal: User | None = None,
    *,
    name: str = "Test Workspace",
    organization: Organization | None = None,
    **kwargs,
) -> Workspace:
    """Create a Workspace (and, if needed, its Organization) for tests.

    Workspaces always belong to an organization, so tests that don't care about
    the organization can omit it and get a default one. Pass ``principal`` to go
    through ``create_if_has_perm`` (which also provisions the database/bucket, so
    callers usually patch those); omit it for a plain ``create``.
    """
    if organization is None:
        organization = Organization.objects.create(name=f"{name} Organization")
    if principal is not None:
        return Workspace.objects.create_if_has_perm(
            principal, name=name, organization=organization, **kwargs
        )
    return Workspace.objects.create(name=name, organization=organization, **kwargs)
