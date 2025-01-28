from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.test import override_settings
from django.utils.crypto import get_random_string

from hexa.core.test import TestCase
from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.files import storage
from hexa.user_management.models import User
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
    def setUpTestData(cls):
        storage.reset()
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
        self,
        workspace=None,
        user=None,
        name="My dataset",
        description="Description of dataset",
    ):
        workspace = workspace or self.WORKSPACE
        user = user or self.USER_ADMIN
        with self.assertRaises(PermissionDenied):
            Dataset.objects.create_if_has_perm(
                self.USER_SERENA,
                self.WORKSPACE,
                name=name,
                description=description,
            )
        dataset = Dataset.objects.create_if_has_perm(
            user,
            workspace,
            name=name,
            description=description,
        )

        self.assertEqual(dataset.name, name)
        self.assertEqual(dataset.description, description)
        self.assertEqual(dataset.created_by, user)

        return dataset

    def test_create_dataset_long_slug(self):
        name = get_random_string(300)

        dataset_1 = self.test_create_dataset(
            workspace=self.WORKSPACE, name=name, description="description_1"
        )
        with patch("secrets.token_hex", return_value="123"):
            dataset_2 = self.test_create_dataset(
                workspace=self.WORKSPACE, name=name, description="description_1"
            )
        self.assertTrue(len(dataset_1.slug) <= 255)
        self.assertTrue(len(dataset_2.slug) <= 255)

        self.assertNotEqual(dataset_1.slug, dataset_2.slug)
        self.assertTrue(dataset_2.slug.endswith("-123"))

    def test_create_dataset_duplicate_slug_same_workspace(self):
        dataset_1 = self.test_create_dataset(
            workspace=self.WORKSPACE, name="my-slug", description="description_1"
        )
        with patch("secrets.token_hex", return_value="123"):
            dataset_2 = self.test_create_dataset(
                workspace=self.WORKSPACE, name="my-slug", description="description_1"
            )
        self.assertNotEqual(dataset_1.slug, dataset_2.slug)
        self.assertEqual(dataset_2.slug, "my-slug-123")

    def test_create_dataset_duplicate_slug(self):
        dataset_1 = self.test_create_dataset(
            workspace=self.WORKSPACE, name="dataset_1", description="description_1"
        )
        dataset_2 = self.test_create_dataset(
            workspace=self.WORKSPACE_2, name="dataset_1", description="description_1"
        )
        self.assertEqual(dataset_1.slug, dataset_2.slug)

    def test_create_dataset_with_double_dash(self):
        dataset = self.test_create_dataset(name="My dataset -- test-")
        self.assertEqual(dataset.slug, "my-dataset-test")

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
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()
        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="My Dataset",
            description="Description of dataset",
        )

        storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)

    def test_create_dataset_version(
        self, name="Dataset's version", changelog="Version's description"
    ):
        with self.assertRaises(PermissionDenied):
            self.DATASET.create_version(
                principal=self.USER_SERENA,
                name="New name",
                changelog="New changelog",
            )

        version = self.DATASET.create_version(
            principal=self.USER_ADMIN,
            name=name,
            changelog=changelog,
        )

        self.assertEqual(version.name, name)
        self.assertEqual(version.changelog, changelog)
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
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()
        storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)

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


class DatasetVersionUpdateTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()
        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="My Dataset",
            description="Description of dataset",
        )

    def test_create_dataset_version(self):
        version = self.DATASET.create_version(
            principal=self.USER_ADMIN,
            name="v1",
            changelog="Version 1 changelog",
        )
        self.assertEqual(version.name, "v1")
        self.assertEqual(version.changelog, "Version 1 changelog")
        return version

    def test_update_dataset_version(self):
        version = self.test_create_dataset_version()
        self.assertNotEqual(version.name, "New name")
        self.assertNotEqual(version.changelog, "New changelog")
        version.update_if_has_perm(
            principal=self.USER_ADMIN, name="New name", changelog="New changelog"
        )
        self.assertEqual(version.name, "New name")
        self.assertEqual(version.changelog, "New changelog")

    def test_update_dataset_version_permission_denied(self):
        version = self.test_create_dataset_version()
        with self.assertRaises(PermissionDenied):
            version.update_if_has_perm(
                principal=self.USER_SERENA, name="New name", changelog="New changelog"
            )
        self.assertNotEqual(version.name, "New name")
        self.assertNotEqual(version.changelog, "New changelog")
