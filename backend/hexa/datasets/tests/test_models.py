from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.test import override_settings
from django.utils.crypto import get_random_string

from hexa.core.test import TestCase
from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.files import storage
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class BaseTestMixin:
    USER_SERENA = None
    USER_VIEWER = None
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
        cls.USER_VIEWER = User.objects.create_user(
            "viewer@bluesquarehub.com", "goodbyequentin"
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
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
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

    def test_update_dataset_version_not_latest_only(self):
        version1 = self.DATASET.create_version(
            principal=self.USER_ADMIN,
            name="v1",
            changelog="Version 1 changelog",
        )
        version2 = self.DATASET.create_version(
            principal=self.USER_ADMIN,
            name="v2",
            changelog="Version 2 changelog",
        )
        version1.update_if_has_perm(
            principal=self.USER_ADMIN,
            name="Updated v1",
            changelog="Updated changelog v1",
        )
        version2.update_if_has_perm(
            principal=self.USER_ADMIN,
            name="Updated v2",
            changelog="Updated changelog v2",
        )
        self.assertEqual(version1.name, "Updated v1")
        self.assertEqual(version2.name, "Updated v2")
        with self.assertRaises(PermissionDenied):
            version2.update_if_has_perm(
                principal=self.USER_VIEWER,
                name="Updated v3",
                changelog="Updated changelog v3",
            )


class DatasetOrganizationSharingTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()

        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org",
            organization_type="CORPORATE",
        )

        cls.ORGANIZATION_2 = Organization.objects.create(
            name="Another Organization",
            short_name="another-org",
            organization_type="ACADEMIC",
        )

        cls.WORKSPACE.organization = cls.ORGANIZATION
        cls.WORKSPACE.save()
        cls.WORKSPACE_2.organization = cls.ORGANIZATION_2
        cls.WORKSPACE_2.save()

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_EDITOR,
            role=OrganizationMembershipRole.MEMBER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_VIEWER,
            role=OrganizationMembershipRole.MEMBER,
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION_2,
            user=cls.USER_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )

        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="My Dataset",
            description="Description of dataset",
        )

    def test_dataset_shared_with_organization_field_defaults_to_false(self):
        self.assertFalse(self.DATASET.shared_with_organization)

    def test_dataset_shared_with_organization_can_be_set_to_true(self):
        self.DATASET.shared_with_organization = True
        self.DATASET.save()
        self.DATASET.refresh_from_db()
        self.assertTrue(self.DATASET.shared_with_organization)

    def test_dataset_filter_for_user_includes_organization_shared_datasets(self):
        org_dataset = Dataset.objects.create_if_has_perm(
            self.USER_ADMIN,
            self.WORKSPACE,
            name="Org Dataset",
            description="Organization shared dataset",
        )
        org_dataset.shared_with_organization = True
        org_dataset.save()

        datasets = Dataset.objects.filter_for_user(self.USER_EDITOR)
        self.assertIn(org_dataset, datasets)

        datasets = Dataset.objects.filter_for_user(self.USER_VIEWER)
        self.assertIn(org_dataset, datasets)

    def test_dataset_filter_for_user_excludes_non_organization_members(self):
        org_dataset = Dataset.objects.create_if_has_perm(
            self.USER_ADMIN,
            self.WORKSPACE,
            name="Org Dataset",
            description="Organization shared dataset",
        )
        org_dataset.shared_with_organization = True
        org_dataset.save()

        datasets = Dataset.objects.filter_for_user(self.USER_SERENA)
        self.assertNotIn(org_dataset, datasets)

    def test_dataset_filter_for_user_excludes_non_shared_datasets(self):
        other_workspace = Workspace.objects.create_if_has_perm(
            self.USER_ADMIN,
            name="Other Workspace",
            description="Workspace USER_EDITOR is not a member of",
            organization=self.ORGANIZATION,
        )

        private_dataset = Dataset.objects.create_if_has_perm(
            self.USER_ADMIN,
            other_workspace,
            name="Private Dataset",
            description="Private dataset",
        )

        datasets = Dataset.objects.filter_for_user(self.USER_EDITOR)
        self.assertNotIn(private_dataset, datasets)

    def test_dataset_filter_for_user_different_organization(self):
        different_org_workspace = Workspace.objects.create_if_has_perm(
            self.USER_ADMIN,
            name="Different Org Workspace",
            description="Workspace in different org",
            organization=self.ORGANIZATION_2,
        )

        different_org_dataset = Dataset.objects.create_if_has_perm(
            self.USER_ADMIN,
            different_org_workspace,
            name="Different Org Dataset",
            description="Dataset in different organization",
        )
        different_org_dataset.shared_with_organization = True
        different_org_dataset.save()

        datasets = Dataset.objects.filter_for_user(self.USER_EDITOR)
        self.assertNotIn(different_org_dataset, datasets)

    def test_update_dataset_shared_with_organization_field(self):
        self.assertFalse(self.DATASET.shared_with_organization)

        self.DATASET.update_if_has_perm(
            principal=self.USER_ADMIN,
            shared_with_organization=True,
        )

        self.DATASET.refresh_from_db()
        self.assertTrue(self.DATASET.shared_with_organization)


class DatasetOrganizationSharingPermissionsTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()

        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-perm",
            organization_type="CORPORATE",
        )

        cls.WORKSPACE.organization = cls.ORGANIZATION
        cls.WORKSPACE.save()

        cls.ORG_MEMBER_USER = User.objects.create_user(
            "org_member@bluesquarehub.com", "password"
        )
        cls.ORG_ADMIN_USER = User.objects.create_user(
            "org_admin@bluesquarehub.com", "password"
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_MEMBER_USER,
            role=OrganizationMembershipRole.MEMBER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_ADMIN_USER,
            role=OrganizationMembershipRole.ADMIN,
        )

        cls.ORG_DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="Org Shared Dataset",
            description="Dataset shared with organization",
        )
        cls.ORG_DATASET.shared_with_organization = True
        cls.ORG_DATASET.save()

    def test_organization_admin_can_update_dataset_organization_sharing(self):
        self.assertTrue(
            self.ORG_ADMIN_USER.has_perm("datasets.update_dataset", self.ORG_DATASET)
        )

    def test_workspace_admin_can_update_dataset_organization_sharing(self):
        self.assertTrue(
            self.USER_ADMIN.has_perm("datasets.update_dataset", self.ORG_DATASET)
        )

    def test_non_organization_member_cannot_update_dataset_organization_sharing(self):
        self.assertFalse(
            self.USER_SERENA.has_perm("datasets.update_dataset", self.ORG_DATASET)
        )

    def test_organization_members_can_view_organization_shared_dataset(self):
        self.assertTrue(
            self.ORG_MEMBER_USER.has_perm("datasets.view_dataset", self.ORG_DATASET)
        )
        self.assertTrue(
            self.ORG_ADMIN_USER.has_perm("datasets.view_dataset", self.ORG_DATASET)
        )

    def test_non_organization_members_cannot_view_organization_shared_dataset(self):
        self.assertFalse(
            self.USER_SERENA.has_perm("datasets.view_dataset", self.ORG_DATASET)
        )

    def test_organization_members_can_download_organization_shared_dataset(self):
        version = self.ORG_DATASET.create_version(
            principal=self.USER_ADMIN,
            name="v1",
            changelog="Version 1",
        )

        self.assertTrue(
            self.ORG_MEMBER_USER.has_perm("datasets.download_dataset_version", version)
        )
        self.assertTrue(
            self.ORG_ADMIN_USER.has_perm("datasets.download_dataset_version", version)
        )

    def test_non_organization_members_cannot_download_organization_shared_dataset(self):
        version = self.ORG_DATASET.create_version(
            principal=self.USER_ADMIN,
            name="v1",
            changelog="Version 1",
        )

        self.assertFalse(
            self.USER_SERENA.has_perm("datasets.download_dataset_version", version)
        )

    def test_non_shared_dataset_organization_permissions(self):
        regular_dataset = Dataset.objects.create_if_has_perm(
            self.USER_ADMIN,
            self.WORKSPACE,
            name="Regular Dataset",
            description="Non-shared dataset",
        )
        self.assertFalse(
            self.ORG_MEMBER_USER.has_perm("datasets.view_dataset", regular_dataset)
        )
        self.assertTrue(
            self.ORG_ADMIN_USER.has_perm("datasets.view_dataset", regular_dataset)
        )

    def test_workspace_level_permissions_still_work_with_organization_sharing(self):
        workspace_dataset = Dataset.objects.create_if_has_perm(
            self.USER_ADMIN,
            self.WORKSPACE,
            name="Workspace Dataset",
            description="Dataset accessible through workspace membership",
        )

        self.assertTrue(
            self.USER_EDITOR.has_perm("datasets.view_dataset", self.ORG_DATASET)
        )
        self.assertTrue(
            self.USER_EDITOR.has_perm("datasets.view_dataset", workspace_dataset)
        )


class DatasetOrganizationAdminOwnerPermissionsTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        BaseTestMixin.setUpTestData()

        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-admin-owner",
            organization_type="CORPORATE",
        )

        cls.ORG_OWNER_USER = User.objects.create_user(
            "owner@bluesquarehub.com", "password"
        )
        cls.ORG_ADMIN_USER = User.objects.create_user(
            "admin@bluesquarehub.com", "password"
        )
        cls.ORG_MEMBER_USER = User.objects.create_user(
            "member@bluesquarehub.com", "password"
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_OWNER_USER,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_ADMIN_USER,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_MEMBER_USER,
            role=OrganizationMembershipRole.MEMBER,
        )

        cls.WORKSPACE.organization = cls.ORGANIZATION
        cls.WORKSPACE.save()

        cls.WORKSPACE_3 = Workspace.objects.create_if_has_perm(
            cls.ORG_OWNER_USER,
            name="Workspace 3",
            description="Another workspace in same org",
            organization=cls.ORGANIZATION,
        )

        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE_3,
            user=cls.USER_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.DATASET_WORKSPACE = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="Dataset in workspace",
            description="Dataset in workspace where org admin/owner is not a member",
        )

        cls.DATASET_WORKSPACE_3 = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE_3,
            name="Dataset in workspace 3",
            description="Dataset in another workspace in same org",
        )

    def test_organization_owner_can_access_all_datasets_in_organization(self):
        datasets = Dataset.objects.filter_for_user(self.ORG_OWNER_USER)

        self.assertIn(self.DATASET_WORKSPACE, datasets)
        self.assertIn(self.DATASET_WORKSPACE_3, datasets)

    def test_organization_admin_can_access_all_datasets_in_organization(self):
        datasets = Dataset.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.DATASET_WORKSPACE, datasets)
        self.assertIn(self.DATASET_WORKSPACE_3, datasets)

    def test_organization_member_cannot_access_datasets_from_non_member_workspaces(
        self,
    ):
        datasets = Dataset.objects.filter_for_user(self.ORG_MEMBER_USER)

        self.assertNotIn(self.DATASET_WORKSPACE, datasets)
        self.assertNotIn(self.DATASET_WORKSPACE_3, datasets)

    def test_organization_owner_can_access_datasets_via_filter_for_workspace_slugs(
        self,
    ):
        workspace_slugs = [self.WORKSPACE.slug, self.WORKSPACE_3.slug]
        datasets = Dataset.objects.filter_for_workspace_slugs(
            self.ORG_OWNER_USER, workspace_slugs
        )

        self.assertIn(self.DATASET_WORKSPACE, datasets)
        self.assertIn(self.DATASET_WORKSPACE_3, datasets)

    def test_organization_admin_can_access_datasets_via_filter_for_workspace_slugs(
        self,
    ):
        workspace_slugs = [self.WORKSPACE.slug, self.WORKSPACE_3.slug]
        datasets = Dataset.objects.filter_for_workspace_slugs(
            self.ORG_ADMIN_USER, workspace_slugs
        )

        self.assertIn(self.DATASET_WORKSPACE, datasets)
        self.assertIn(self.DATASET_WORKSPACE_3, datasets)

    def test_organization_member_cannot_access_datasets_via_filter_for_workspace_slugs(
        self,
    ):
        workspace_slugs = [self.WORKSPACE.slug, self.WORKSPACE_3.slug]
        datasets = Dataset.objects.filter_for_workspace_slugs(
            self.ORG_MEMBER_USER, workspace_slugs
        )

        self.assertNotIn(self.DATASET_WORKSPACE, datasets)
        self.assertNotIn(self.DATASET_WORKSPACE_3, datasets)

    def test_dataset_links_access(self):
        expected_links = DatasetLink.objects.filter(
            workspace__organization=self.ORGANIZATION
        )

        owner_dataset_links = DatasetLink.objects.filter_for_user(self.ORG_OWNER_USER)
        admin_dataset_links = DatasetLink.objects.filter_for_user(self.ORG_ADMIN_USER)
        member_dataset_links = DatasetLink.objects.filter_for_user(self.ORG_MEMBER_USER)

        for link in expected_links:
            self.assertIn(link, owner_dataset_links)
            self.assertIn(link, admin_dataset_links)
            self.assertNotIn(link, member_dataset_links)

    def test_organization_admin_owner_access_combined_with_workspace_membership(self):
        WorkspaceMembership.objects.create(
            workspace=self.WORKSPACE,
            user=self.ORG_ADMIN_USER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        datasets = Dataset.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.DATASET_WORKSPACE, datasets)
        self.assertIn(self.DATASET_WORKSPACE_3, datasets)

    def test_organization_shared_dataset_plus_admin_owner_permissions(self):
        self.DATASET_WORKSPACE.shared_with_organization = True
        self.DATASET_WORKSPACE.save()

        datasets_owner = Dataset.objects.filter_for_user(self.ORG_OWNER_USER)
        datasets_admin = Dataset.objects.filter_for_user(self.ORG_ADMIN_USER)
        datasets_member = Dataset.objects.filter_for_user(self.ORG_MEMBER_USER)

        self.assertIn(self.DATASET_WORKSPACE, datasets_owner)
        self.assertIn(self.DATASET_WORKSPACE, datasets_admin)
        self.assertIn(self.DATASET_WORKSPACE, datasets_member)
