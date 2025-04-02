from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

from ..models import Dataset, DatasetVersion, DatasetVersionFile


class DatasetTestMixin:
    def create_user(self, email, *args, password=None, **kwargs):
        password = password or "Pa$$w0rd"
        user = User.objects.create_user(email, *args, password=password, **kwargs)
        return user

    def create_workspace(self, principal: User, name, description, *args, **kwargs):
        workspace = Workspace.objects.create_if_has_perm(
            principal=principal, name=name, description=description, *args, **kwargs
        )
        return workspace

    def join_workspace(
        self, user: User, workspace: Workspace, role: WorkspaceMembershipRole
    ):
        membership, created = WorkspaceMembership.objects.get_or_create(
            workspace=workspace, user=user, defaults={"role": role}
        )
        if not created:
            membership.role = role
        return membership

    def create_dataset(
        self, principal: User, workspace: Workspace, name, description, *args, **kwargs
    ):
        dataset = Dataset.objects.create_if_has_perm(
            principal=principal,
            workspace=workspace,
            name=name,
            description=description,
            *args,
            **kwargs,
        )
        return dataset

    @staticmethod
    def create_dataset_version(
        principal: User, *, dataset: Dataset, name="v1", changelog=None, **kwargs
    ) -> DatasetVersion:
        return DatasetVersion.objects.create_if_has_perm(
            principal=principal,
            dataset=dataset,
            name=name,
            changelog=changelog,
            **kwargs,
        )

    @staticmethod
    def create_dataset_version_file(
        principal: User,
        *,
        dataset_version: DatasetVersion,
        uri: str = "some-uri.csv",
        content_type="text/csv",
        **kwargs,
    ) -> DatasetVersionFile:
        return DatasetVersionFile.objects.create_if_has_perm(
            principal=principal,
            dataset_version=dataset_version,
            uri=uri,
            **kwargs,
            content_type=content_type,
        )
