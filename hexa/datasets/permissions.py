from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


def create_dataset(principal: User, workspace: Workspace):
    """Only workspace admins & editors can create datasets"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()


def update_dataset(principal, dataset: Dataset):
    """Only workspace admins can update datasets"""
    return create_dataset(principal, dataset.workspace)


def delete_dataset(principal: User, dataset: Dataset):
    """Only workspace admins can delete datasets"""
    return create_dataset(principal, dataset.workspace)


def create_dataset_version(principal: User, dataset: Dataset):
    """Only workspace admins & editors can create dataset versions"""
    return create_dataset(principal, dataset.workspace)


def update_dataset_version(principal: User, version: DatasetVersion):
    """Only workspace admins & editors can update dataset versions and
    only the latest version can be updated
    """
    return (
        create_dataset(principal, version.dataset.workspace)
        and version.dataset.latest_version == version
    )


def delete_dataset_version(principal: User, version: DatasetVersion):
    """Only workspace admins can delete dataset versions"""
    return create_dataset(principal, version.dataset.workspace)


def download_dataset_version(principal: User, version: DatasetVersion):
    """Only workspace members can download dataset versions.
    This also includes members of workspaces that have been shared this dataset.
    """
    return version.dataset.links.filter(
        workspace__in=principal.workspace_set.all()
    ).exists()


def view_dataset(principal: User, dataset: Dataset):
    """Only workspace members can view dataset.
    This also includes members of workspaces that have been shared this dataset.
    """
    return (
        dataset.links.filter(workspace__in=principal.workspace_set.all()).exists()
        or dataset.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
    )


def link_dataset(principal: User, datasetAndWorkspace):
    dataset, workspace = datasetAndWorkspace
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
