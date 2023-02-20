from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from hexa.core.test import TestCase
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
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
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_JULIA
        )

    def test_create_workspace_regular_user(self):
        with self.assertRaises(PermissionDenied):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_SERENA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )
            workspace.save()

    def test_create_workspace_no_slug(self):
        with patch("secrets.token_hex", lambda _: "mock"):
            with patch("hexa.workspaces.models.create_database"):
                workspace = Workspace.objects.create_if_has_perm(
                    self.USER_JULIA,
                    name="this is a very long workspace name",
                    description="Description",
                )
        self.assertEqual(workspace.slug, "this-is-a-very-long-wor-mock")
        self.assertTrue(len(workspace.slug) <= 30)

    def test_create_workspace_with_underscore(self):
        with patch("secrets.token_hex", lambda _: "mock"):
            with patch("hexa.workspaces.models.create_database"):
                workspace = Workspace.objects.create_if_has_perm(
                    self.USER_JULIA,
                    name="Worksp?ace_wi😱th_und~ersc!/ore",
                    description="Description",
                )
        self.assertEqual(workspace.slug, "worksp-ace-with-und-er-mock")

    def test_create_workspace_admin_user(self):
        workspace = Workspace.objects.create_if_has_perm(
            self.USER_JULIA,
            name="Senegal Workspace",
            description="This is test for creating workspace",
        )
        workspace.save()
        self.assertEqual(1, Workspace.objects.all().count())

    def test_get_workspace_by_id(self):
        workspace = Workspace.objects.create_if_has_perm(
            self.USER_JULIA,
            name="Senegal Workspace",
            description="This is test for creating workspace",
        )
        workspace.save()
        self.assertEqual(workspace, Workspace.objects.get(id=workspace.id))

    def test_get_workspace_by_id_failed(self):
        with self.assertRaises(ObjectDoesNotExist):
            Workspace.objects.get(pk="7bf4c750-f74b-4ed6-b7f7-b23e4cac4e2c")

    def test_add_member(self):
        workspace = Workspace.objects.create_if_has_perm(
            self.USER_JULIA,
            name="Senegal Workspace",
            description="This is test for creating workspace",
        )
        workspace.save()
        self.assertTrue(
            WorkspaceMembership.objects.filter(
                user=self.USER_JULIA,
                workspace=workspace,
                role=WorkspaceMembershipRole.ADMIN,
            ).exists()
        )


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
            role=WorkspaceMembershipRole.EDITOR,
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

    def test_create_connection_editor_member(self):
        with self.assertRaises(PermissionDenied):
            Connection.objects.create_if_has_perm(
                self.USER_JIM,
                self.WORKSPACE,
                name="Connection",
                slug="conn",
                connection_type=ConnectionType.CUSTOM,
            )

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
