import base64

from hexa.datasets.models import Dataset, DatasetVersion
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class MetadataTestMixin:
    def create_user(self, email, *args, password=None, **kwargs):
        password = password or "Pa$$w0rd"
        user = User.objects.create_user(email, *args, password=password, **kwargs)
        return user

    @staticmethod
    def create_feature_flag(*, code: str, user: User):
        feature, _ = Feature.objects.get_or_create(code=code)
        FeatureFlag.objects.create(feature=feature, user=user)

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


def encode_base_64(data):
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def decode_base_64(data):
    return base64.b64decode(data.encode("utf-8")).decode("utf-8")
