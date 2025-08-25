from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.user_management.models import (
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


def create_dataset(principal: User, workspace: Workspace):
    """Only workspace admins & editors can create datasets"""
    # Check workspace membership
    if workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists():
        return True

    # Check organization membership
    if workspace.organization:
        return workspace.organization.organizationmembership_set.filter(
            user=principal,
            role__in=[
                OrganizationMembershipRole.ADMIN,
                OrganizationMembershipRole.OWNER,
            ],
        ).exists()

    return False


def update_dataset(principal: User, dataset: Dataset):
    """Only workspace admins can update datasets"""
    return create_dataset(principal, dataset.workspace)


def delete_dataset(principal: User, dataset: Dataset):
    """Only workspace admins can delete datasets"""
    return create_dataset(principal, dataset.workspace)


def create_dataset_version(principal: User, dataset: Dataset):
    """Only workspace admins & editors can create dataset versions"""
    return create_dataset(principal, dataset.workspace)


def update_dataset_version(principal: User, version: DatasetVersion):
    """Only workspace admins & editors can update dataset versions"""
    return create_dataset(principal, version.dataset.workspace)


def delete_dataset_version(principal: User, version: DatasetVersion):
    """Only workspace admins can delete dataset versions"""
    return create_dataset(principal, version.dataset.workspace)


def download_dataset_version(principal: User, version: DatasetVersion):
    """Only workspace members can download dataset versions.
    This also includes members of workspaces that have been shared this dataset
    and organization members for organization-shared datasets.
    """
    # Check if user is a member of the dataset's workspace
    if version.dataset.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists():
        return True

    # Check if user has access through workspace links
    if version.dataset.links.filter(
        workspace__in=principal.workspace_set.all()
    ).exists():
        return True

    # Check if user has access through organization sharing
    if (
        version.dataset.shared_with_organization
        and version.dataset.workspace.organization
    ):
        return version.dataset.workspace.organization.organizationmembership_set.filter(
            user=principal
        ).exists()

    return False


def view_dataset(principal: User, dataset: Dataset):
    """Users can view datasets if they are workspace members, have access through dataset links,
    or have access through organization sharing.
    """
    # Check if user has access through dataset links to their workspaces
    if dataset.links.filter(workspace__in=principal.workspace_set.all()).exists():
        return True

    # Check if user is a member of the dataset's workspace
    if dataset.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists():
        return True

    # Check if user has access through organization sharing
    if dataset.shared_with_organization and dataset.workspace.organization:
        return dataset.workspace.organization.organizationmembership_set.filter(
            user=principal
        ).exists()

    return False


def link_dataset(principal: User, dataset_and_workspace):
    dataset, workspace = dataset_and_workspace
    """
    A user can link a dataset with a workspace if:
    - they are a member of the workspace as an admin or editor
    - the dataset is already linked to one of their workspaces
    """

    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() and principal.has_perm("datasets.view_dataset", dataset)


def delete_dataset_link(principal: User, link: DatasetLink):
    """Editors & admins from the source workspace can delete any link and
    editors & admins from the target workspace can delete links from their workspace
    """
    return WorkspaceMembership.objects.filter(
        workspace__in=[link.dataset.workspace, link.workspace],
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()


def pin_dataset(principal: User, link: DatasetLink):
    """Only workspace admins & editors can pin datasets from the dataset"""
    return link.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()


def create_dataset_version_file(principal: User, dataset_version: DatasetVersion):
    if dataset_version != dataset_version.dataset.latest_version:
        return False

    return create_dataset_version(principal, dataset_version.dataset)


def delete_dataset_version_file(principal: User, version: DatasetVersionFile):
    return delete_dataset_version(principal, version.dataset_version)


def update_dataset_version_file(principal: User, dataset_version: DatasetVersionFile):
    return update_dataset_version(principal, dataset_version.dataset_version)


def view_dataset_version_file(
    principal: User, dataset_version_file: DatasetVersionFile
):
    return view_dataset_version(principal, dataset_version_file.dataset_version)


def view_dataset_version(principal: User, version: DatasetVersion):
    return view_dataset(principal, version.dataset)
