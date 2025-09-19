import hashlib
import uuid
from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.test import override_settings

from hexa.core.test import TestCase
from hexa.files import storage
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceTest(TestCase):
    USER_SERENA = None
    USER_JULIA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces.prevent_create"),
            user=cls.USER_SERENA,
        )

    def setUp(self) -> None:
        storage.reset()
        return super().setUp()

    def test_create_workspace_prevent_create_flag(self):
        with self.assertRaises(PermissionDenied):
            Workspace.objects.create_if_has_perm(
                self.USER_SERENA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )

    def test_create_workspace_no_slug(self):
        with (
            patch("secrets.token_hex", lambda _: "mock"),
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="this is a very long workspace name",
                description="Description",
            )
        self.assertEqual(workspace.slug, "this-is-a-very-long-workspace-name")
        self.assertTrue(len(workspace.slug) <= 63)

    def test_create_workspace_with_underscore(self):
        with (
            patch("secrets.token_hex", lambda _: "mock"),
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Worksp?ace_wi😱th_und~ersc!/ore",
                description="Description",
            )

        self.assertEqual(workspace.slug, "worksp-ace-with-und-ersc-ore")
        self.assertTrue(storage.bucket_exists(workspace.bucket_name))

    def test_create_workspace_with_random_characters(self):
        with (
            patch("secrets.token_hex", lambda _: "mock"),
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="1workspace_with#_random$_char*",
                description="Description",
            )
        self.assertEqual(workspace.slug, "1workspace-with-random-char")
        self.assertEqual(16, len(workspace.db_name))

    def test_create_workspace_admin_user(self):
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )
        self.assertEqual(1, Workspace.objects.all().count())

    def test_get_workspace_by_id(self):
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )
            self.assertEqual(workspace, Workspace.objects.get(id=workspace.id))

    def test_get_workspace_by_id_failed(self):
        with self.assertRaises(ObjectDoesNotExist):
            Workspace.objects.get(pk="7bf4c750-f74b-4ed6-b7f7-b23e4cac4e2c")

    def test_create_workspaces_same_name(self):
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
            patch("secrets.token_hex", lambda _: "mock"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="My workspace",
                description="This is my workspace",
            )
            self.assertEqual(workspace.slug, "my-workspace")

            workspace_2 = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="My workspace",
                description="This is my workspace",
            )

            self.assertEqual(workspace_2.slug, "my-workspace-mock")

    def test_add_member(self):
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )
            self.assertTrue(
                WorkspaceMembership.objects.filter(
                    user=self.USER_JULIA,
                    workspace=workspace,
                    role=WorkspaceMembershipRole.ADMIN,
                ).exists()
            )
            self.assertEqual(
                hashlib.blake2s(
                    f"{workspace.id}_{self.USER_JULIA.id}".encode(),
                    digest_size=16,
                ).hexdigest(),
                WorkspaceMembership.objects.get(
                    user=self.USER_JULIA, workspace=workspace
                ).notebooks_server_hash,
            )

    def test_organization_membership_created(self):
        organization = Organization.objects.create(name="Test Organization")
        workspace = Workspace.objects.create(
            name="Test Workspace",
            slug="test-workspace",
            organization=organization,
        )

        self.assertFalse(
            OrganizationMembership.objects.filter(
                organization=organization, user=self.USER_SERENA
            ).exists()
        )

        WorkspaceMembership.objects.create(
            user=self.USER_SERENA,
            workspace=workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )

        membership = OrganizationMembership.objects.get(
            organization=organization, user=self.USER_SERENA
        )
        self.assertIsNotNone(membership)
        self.assertEqual(membership.role, OrganizationMembershipRole.MEMBER)

    def test_add_external_user(self):
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )

            invitation = WorkspaceInvitation.objects.create_if_has_perm(
                principal=self.USER_JULIA,
                workspace=workspace,
                email="john@doe.com",
                role=WorkspaceMembershipRole.VIEWER,
            )
            self.assertIsInstance(invitation, WorkspaceInvitation)
            self.assertEqual(invitation.status, WorkspaceInvitationStatus.PENDING)
            self.assertEqual(invitation.invited_by, self.USER_JULIA)

    def test_workspace_configuration_default(self):
        """Test that workspace configuration field has a default empty dict"""
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Test Workspace",
                description="Test workspace for configuration",
            )
        self.assertEqual(workspace.configuration, {})

    def test_workspace_configuration_set_and_update(self):
        """Test that workspace configuration can be set and updated"""
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Test Workspace",
                description="Test workspace for configuration",
            )

        initial_config = {"api_key": "test123", "timeout": 30}
        workspace.update_if_has_perm(
            principal=self.USER_JULIA, configuration=initial_config
        )
        workspace.refresh_from_db()
        self.assertEqual(workspace.configuration, initial_config)

        updated_config = {"api_key": "updated456", "timeout": 60, "new_setting": True}
        workspace.update_if_has_perm(
            principal=self.USER_JULIA, configuration=updated_config
        )
        workspace.refresh_from_db()
        self.assertEqual(workspace.configuration, updated_config)

    def test_workspace_configuration_permission_denied(self):
        """Test that non-admin users cannot update configuration"""
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Test Workspace",
                description="Test workspace for configuration",
            )

        WorkspaceMembership.objects.create(
            user=self.USER_SERENA,
            workspace=workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )

        with self.assertRaises(PermissionDenied):
            workspace.update_if_has_perm(
                principal=self.USER_SERENA, configuration={"unauthorized": "update"}
            )

    def test_workspace_configuration_editor_can_update(self):
        """Test that editor users can update configuration"""
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_JULIA,
                name="Test Workspace",
                description="Test workspace for configuration",
            )

        WorkspaceMembership.objects.create(
            user=self.USER_SERENA,
            workspace=workspace,
            role=WorkspaceMembershipRole.EDITOR,
        )

        editor_config = {"editor_setting": "value_from_editor"}
        workspace.update_if_has_perm(
            principal=self.USER_SERENA, configuration=editor_config
        )
        workspace.refresh_from_db()
        self.assertEqual(workspace.configuration, editor_config)

    @override_settings(
        WORKSPACES_DATABASE_PROXY_HOST="db.proxy", OVERRIDE_WORKSPACES_DATABASE_HOST=""
    )
    def test_db_host_default_behavior(self):
        """Test db_host property returns default proxy host format when override is empty"""
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(self.USER_JULIA, name="WP")

        self.assertEqual(workspace.db_host, f"{workspace.slug}.db.proxy")

    @override_settings(
        WORKSPACES_DATABASE_PROXY_HOST="db.proxy",
        OVERRIDE_WORKSPACES_DATABASE_HOST="192.168.1.100",
    )
    def test_db_host_override_behavior(self):
        """Test db_host property returns override host when OVERRIDE_WORKSPACES_DATABASE_HOST is set"""
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            workspace = Workspace.objects.create_if_has_perm(self.USER_JULIA, name="WP")

        self.assertEqual(workspace.db_host, "192.168.1.100")


class WorkspaceOrganizationRoleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com",
            "admin",
            analytics_enabled=True,
            is_superuser=True,
        )

        cls.organization = Organization.objects.create(name="Test Organization")

        cls.org_owner = User.objects.create_user("owner@example.com", "password")
        cls.org_admin = User.objects.create_user("admin@example.com", "password")
        cls.org_member = User.objects.create_user("member@example.com", "password")
        cls.external_user = User.objects.create_user("external@example.com", "password")

        OrganizationMembership.objects.create(
            organization=cls.organization,
            user=cls.org_owner,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.organization,
            user=cls.org_admin,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.organization,
            user=cls.org_member,
            role=OrganizationMembershipRole.MEMBER,
        )

        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.org_workspace = Workspace.objects.create_if_has_perm(
                principal=cls.USER_ADMIN,
                name="Organization Workspace",
                organization=cls.organization,
            )
            cls.standalone_workspace = Workspace.objects.create_if_has_perm(
                principal=cls.USER_ADMIN,
                name="Standalone Workspace",
            )

        WorkspaceMembership.objects.create(
            user=cls.external_user,
            workspace=cls.standalone_workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_organization_owner_can_access_all_workspaces(self):
        """Organization owners should have access to all workspaces in their organization"""
        accessible_workspaces = Workspace.objects.filter_for_user(self.org_owner)

        self.assertIn(self.org_workspace, accessible_workspaces)
        self.assertNotIn(self.standalone_workspace, accessible_workspaces)

    def test_organization_admin_can_access_all_workspaces(self):
        """Organization admins should have access to all workspaces in their organization"""
        accessible_workspaces = Workspace.objects.filter_for_user(self.org_admin)

        self.assertIn(self.org_workspace, accessible_workspaces)
        self.assertNotIn(self.standalone_workspace, accessible_workspaces)

    def test_organization_member_cannot_access_workspaces_without_membership(self):
        """Organization members should NOT have automatic access to all workspaces"""
        accessible_workspaces = Workspace.objects.filter_for_user(self.org_member)

        self.assertNotIn(self.org_workspace, accessible_workspaces)
        self.assertNotIn(self.standalone_workspace, accessible_workspaces)

    def test_external_user_only_accesses_direct_memberships(self):
        """External users should only access workspaces they're directly members of"""
        accessible_workspaces = Workspace.objects.filter_for_user(self.external_user)

        self.assertNotIn(self.org_workspace, accessible_workspaces)
        self.assertIn(self.standalone_workspace, accessible_workspaces)

    def test_organization_admin_with_workspace_membership(self):
        """Organization admin with explicit workspace membership should have access"""
        WorkspaceMembership.objects.create(
            user=self.org_admin,
            workspace=self.standalone_workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )

        accessible_workspaces = Workspace.objects.filter_for_user(self.org_admin)

        self.assertIn(self.org_workspace, accessible_workspaces)
        self.assertIn(self.standalone_workspace, accessible_workspaces)

    def test_archived_workspace_not_accessible(self):
        """Archived workspaces should not be accessible even for organization admins"""
        self.org_workspace.archived = True
        self.org_workspace.save()

        accessible_workspaces = Workspace.objects.filter_for_user(self.org_owner)

        self.assertNotIn(self.org_workspace, accessible_workspaces)


class ConnectionTest(TestCase):
    USER_SERENA = None
    USER_ADMIN = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )
        cls.USER_JIM = User.objects.create_user("jim@bluesquarehub.com", "jim&password")

        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "admin", is_superuser=True
        )
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN, name="Workspace's title"
            )

        WorkspaceMembership.objects.create(
            user=cls.USER_SERENA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_JIM,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_create_connection_admin_member(self):
        Connection.objects.create_if_has_perm(
            self.USER_SERENA,
            self.WORKSPACE,
            name="Connection",
            slug="conn",
            connection_type=ConnectionType.CUSTOM,
        )

        self.assertEqual(Connection.objects.count(), 1)

    def test_create_connection_viewer_member(self):
        with self.assertRaises(PermissionDenied):
            Connection.objects.create_if_has_perm(
                self.USER_JIM,
                self.WORKSPACE,
                name="Connection",
                slug="conn",
                connection_type=ConnectionType.CUSTOM,
            )

    def test_create_connection_new_slug(self):
        con = Connection.objects.create_if_has_perm(
            self.USER_SERENA,
            self.WORKSPACE,
            name="Connection with a slug",
            connection_type=ConnectionType.CUSTOM,
        )

        self.assertEqual(con.slug, "connection-with-a-slug")

    def test_create_connection_existing_slug(self):
        self.test_create_connection_new_slug()

        slug_uuid = uuid.uuid4()

        with patch("uuid.uuid4", return_value=slug_uuid):
            con = Connection.objects.create_if_has_perm(
                self.USER_SERENA,
                self.WORKSPACE,
                name="connection-with-a slug",
                connection_type=ConnectionType.CUSTOM,
            )

        self.assertEqual(con.slug, f"connection-with-a-slug-{slug_uuid.hex[:4]}")

    def test_add_connection_field(self):
        connection = Connection.objects.create_if_has_perm(
            self.USER_SERENA,
            self.WORKSPACE,
            name="Connection",
            slug="conn",
            connection_type=ConnectionType.CUSTOM,
        )
        connection.set_fields(
            self.USER_SERENA,
            [{"code": "field_1", "value": "value_1", "secret": False}],
        )
        connection.save()

        self.assertEqual(connection.fields.count(), 1)
        field = connection.fields.first()
        self.assertEqual(field.code, "field_1")
        self.assertEqual(field.value, "value_1")
        self.assertEqual(field.secret, False)

    def test_update_connection_fields(self):
        connection = Connection.objects.create_if_has_perm(
            self.USER_SERENA,
            self.WORKSPACE,
            name="Connection",
            slug="conn",
            connection_type=ConnectionType.CUSTOM,
        )
        connection.set_fields(
            self.USER_SERENA,
            [{"code": "field_1", "value": "value_1", "secret": False}],
        )
        connection.save()

        connection.set_fields(
            self.USER_SERENA,
            [
                {
                    "id": str(connection.fields.first().id),
                    "code": "field_1",
                    "value": "new_value_1",
                    "secret": True,
                },
                {"code": "field_2", "value": "value_2", "secret": True},
            ],
        )
        connection.save()

        field_1 = connection.fields.get(code="field_1")
        self.assertEqual(field_1.code, "field_1")
        self.assertEqual(field_1.value, "new_value_1")
        self.assertEqual(field_1.secret, True)

        field_2 = connection.fields.get(code="field_2")
        self.assertTrue(field_2.value, "value_2")

    def test_delete_connection_fields(self):
        connection = Connection.objects.create_if_has_perm(
            self.USER_SERENA,
            self.WORKSPACE,
            name="Connection",
            slug="conn",
            connection_type=ConnectionType.CUSTOM,
        )
        connection.set_fields(
            self.USER_SERENA,
            [{"code": "field_1", "value": "value_1", "secret": False}],
        )
        connection.save()

        self.assertEqual(connection.fields.count(), 1)

        connection.set_fields(self.USER_SERENA, [])
        connection.save()

        self.assertEqual(connection.fields.count(), 0)

    def test_fields_not_updated(self):
        connection = Connection.objects.create_if_has_perm(
            self.USER_SERENA,
            self.WORKSPACE,
            name="Connection",
            slug="conn",
            connection_type=ConnectionType.CUSTOM,
        )
        connection.update_if_has_perm(self.USER_SERENA, name="Connection 2")

        self.assertEqual(connection.fields.count(), 0)
