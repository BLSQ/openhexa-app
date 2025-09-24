from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.user_management.models import (
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


def create_dataset(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def update_dataset(principal: User, dataset: Dataset):
    return create_dataset(principal, dataset.workspace)


def delete_dataset(principal: User, dataset: Dataset):
    return create_dataset(principal, dataset.workspace)


def create_dataset_version(principal: User, dataset: Dataset):
    return create_dataset(principal, dataset.workspace)


def update_dataset_version(principal: User, version: DatasetVersion):
    return create_dataset(principal, version.dataset.workspace)


def delete_dataset_version(principal: User, version: DatasetVersion):
    return create_dataset(principal, version.dataset.workspace)


def download_dataset_version(principal: User, version: DatasetVersion):
    return (
        version.dataset.links.filter(
            workspace__in=principal.workspace_set.all()
        ).exists()
        or (
            version.dataset.shared_with_organization
            and version.dataset.workspace.organization
            and principal.is_organization_member(version.dataset.workspace.organization)
        )
        or principal.is_organization_admin_or_owner(
            version.dataset.workspace.organization
        )
    )


def view_dataset(principal: User, dataset: Dataset):
    return (
        dataset.links.filter(workspace__in=principal.workspace_set.all()).exists()
        or dataset.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
        or (
            dataset.shared_with_organization
            and dataset.workspace.organization
            and principal.is_organization_member(dataset.workspace.organization)
        )
        or principal.is_organization_admin_or_owner(dataset.workspace.organization)
    )


def link_dataset(principal: User, dataset_and_workspace):
    dataset, workspace = dataset_and_workspace
    return (
        workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
        or principal.is_organization_admin_or_owner(workspace.organization)
    ) and principal.has_perm("datasets.view_dataset", dataset)


def delete_dataset_link(principal: User, link: DatasetLink):
    return WorkspaceMembership.objects.filter(
        workspace__in=[link.dataset.workspace, link.workspace],
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(link.workspace.organization)


def pin_dataset(principal: User, link: DatasetLink):
    return link.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(link.workspace.organization)


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
