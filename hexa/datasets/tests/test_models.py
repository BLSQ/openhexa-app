from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.test import override_settings

from hexa.core.test import TestCase
from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.files.api import get_storage
from hexa.files.tests.mocks.mockgcp import backend
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class BaseTestMixin:
    USER_SERENA = None
    USER_EDITOR = None
    WORKSPACE = None

    @classmethod
    @backend.mock_storage
    def setUpTestData(cls):
        backend.reset()
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )
        cls.USER_EDITOR = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "rebecca's password",
        )

        cls.USER_ADMIN = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword", is_superuser=True
        )
        FEATURE = Feature.objects.create(code="workspaces")
        FeatureFlag.objects.create(feature=FEATURE, user=cls.USER_ADMIN)
        FeatureFlag.objects.create(feature=FEATURE, user=cls.USER_SERENA)
        FeatureFlag.objects.create(feature=FEATURE, user=cls.USER_EDITOR)

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN, name="My Workspace", description="Test workspace"
        )
        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN, name="My Workspace 2", description="Test workspace 2"
        )

        cls.USER_ADMIN.is_superuser = False
        cls.USER_ADMIN.save()
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE_2,
            user=cls.USER_SERENA,
            role=WorkspaceMembershipRole.EDITOR,
        )


class DatasetTest(BaseTestMixin, TestCase):
    def test_create_dataset(
        self, workspace=None, name="My dataset", description="Description of dataset"
    ):
        workspace = workspace or self.WORKSPACE
        with self.assertRaises(PermissionDenied):
            Dataset.objects.create_if_has_perm(
                self.USER_SERENA,
                self.WORKSPACE,
                name=name,
                description=description,
            )
        dataset = Dataset.objects.create_if_has_perm(
            self.USER_EDITOR,
            self.WORKSPACE,
            name=name,
            description=description,
        )

        self.assertEqual(dataset.name, name)
        self.assertEqual(dataset.description, description)
        self.assertEqual(dataset.created_by, self.USER_EDITOR)

        return dataset

    def test_create_dataset_with_double_dash(self):
        with patch("secrets.token_hex", return_value="123"):
            dataset = self.test_create_dataset(name="My dataset -- test-")
        self.assertEqual(dataset.slug, "my-dataset-test-123")

    def test_workspace_datasets(self):
        self.test_create_dataset(name="dataset_1", description="description_1")
        self.test_create_dataset(name="dataset_2", description="description_2")

        self.assertEqual(
            self.WORKSPACE.datasets.filter(workspace=self.WORKSPACE).count(), 2
        )
        self.assertEqual(
            self.WORKSPACE_2.datasets.filter(workspace=self.WORKSPACE).count(), 0
        )

    def test_update_dataset(self):
        dataset = self.test_create_dataset()

        dataset.update_if_has_perm(
            principal=self.USER_EDITOR,
            name="New name",
            description="New description",
        )

        with self.assertRaises(PermissionDenied):
            dataset.update_if_has_perm(
                principal=self.USER_SERENA,
                name="New name 2",
                description="New description 2",
            )

        self.assertEqual(dataset.name, "New name")
        self.assertEqual(dataset.description, "New description")

    def test_delete_dataset(self):
        dataset = self.test_create_dataset()

        with self.assertRaises(PermissionDenied):
            dataset.delete_if_has_perm(principal=self.USER_SERENA)

        dataset.delete_if_has_perm(principal=self.USER_EDITOR)
        with self.assertRaises(ObjectDoesNotExist):
            Dataset.objects.get(id=dataset.id)


@override_settings(WORKSPACE_DATASETS_BUCKET="hexa-datasets")
class DatasetVersionTest(BaseTestMixin, TestCase):
    DATASET = None

    @classmethod
    @backend.mock_storage
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()
        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="My Dataset",
            description="Description of dataset",
        )

        get_storage().create_bucket(settings.WORKSPACE_DATASETS_BUCKET)

    @backend.mock_storage
    def test_create_dataset_version(
        self, name="Dataset's version", description="Version's description"
    ):
        with self.assertRaises(PermissionDenied):
            self.DATASET.create_version(
                principal=self.USER_SERENA,
                name="New name",
                description="New description",
                filename="file.txt",
                content_type="text/plain",
            )

        version = self.DATASET.create_version(
            principal=self.USER_ADMIN,
            name=name,
            description=description,
            filename="file.txt",
            content_type="text/plain",
        )

        self.assertEqual(version.name, name)
        self.assertEqual(version.description, description)
        self.assertEqual(self.DATASET.versions.filter(id=version.id).count(), 1)

        return version

    def test_delete_dataset_version(self):
        version = self.test_create_dataset_version()

        with self.assertRaises(PermissionDenied):
            version.delete_if_has_perm(principal=self.USER_SERENA)

        version.delete_if_has_perm(principal=self.USER_EDITOR)
        with self.assertRaises(ObjectDoesNotExist):
            DatasetVersion.objects.get(id=version.id)

    def test_get_file_by_name(self):
        version = self.test_create_dataset_version()
        with self.assertRaises(ObjectDoesNotExist):
            version.get_file_by_name("file.txt")

        DatasetVersionFile.objects.create(
            dataset_version=version,
            uri=version.get_full_uri("file.txt"),
            created_by=self.USER_ADMIN,
            content_type="text/plain",
        )

        self.assertEqual(
            version.get_file_by_name("file.txt").uri,
            f"{version.dataset.id}/{version.id}/file.txt",
        )


@override_settings(WORKSPACE_DATASETS_BUCKET="hexa-datasets")
class DatasetLinkTest(BaseTestMixin, TestCase):
    @classmethod
    @backend.mock_storage
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()
        get_storage().create_bucket(settings.WORKSPACE_DATASETS_BUCKET)

        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="My Dataset",
            description="Description of dataset",
        )

    def test_cannot_link_dataset(self):
        self.assertFalse(
            self.USER_SERENA.has_perm(
                "datasets.link_dataset", (self.DATASET, self.WORKSPACE_2)
            )
        )

    def test_link_dataset(self):
        self.assertFalse(
            self.USER_SERENA.has_perm("datasets.view_dataset", self.DATASET)
        )
        self.assertEqual(self.WORKSPACE_2.datasets.count(), 0)
        self.DATASET.link(self.USER_ADMIN, self.WORKSPACE_2)
        self.assertEqual(self.WORKSPACE_2.datasets.first(), self.DATASET)
        self.assertTrue(
            self.USER_SERENA.has_perm("datasets.view_dataset", self.DATASET)
        )
