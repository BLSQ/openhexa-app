import uuid
from unittest.mock import patch

from django.core.exceptions import PermissionDenied

from hexa.connections.models import Connection, ConnectionType
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
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
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
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
