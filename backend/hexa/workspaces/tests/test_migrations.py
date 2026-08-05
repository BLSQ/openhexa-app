from unittest.mock import patch

from django.test import TransactionTestCase

from hexa.core.test.migrator import Migrator
from hexa.user_management.models import Organization as RealOrganization
from hexa.user_management.models import OrganizationType


class WorkspaceOrganizationRequiredMigrationTest(TransactionTestCase):
    migrate_from = ("workspaces", "0060_grant_create_on_public_to_rw_role")
    migrate_to = ("workspaces", "0061_workspace_organization_required")

    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)

    def _models(self):
        return (
            self.migrator.apps.get_model("workspaces", "Workspace"),
            self.migrator.apps.get_model("workspaces", "WorkspaceMembership"),
            self.migrator.apps.get_model("user_management", "User"),
            self.migrator.apps.get_model("user_management", "Organization"),
            self.migrator.apps.get_model("user_management", "OrganizationMembership"),
        )

    def _create_workspace(self, Workspace, name, slug, archived=False):
        return Workspace.objects.create(
            name=name,
            slug=slug,
            db_name=slug.replace("-", "_"),
            bucket_name=f"bucket-{slug}",
            archived=archived,
        )

    def test_orphans_are_attached_to_default_organization_with_memberships(self):
        (
            Workspace,
            WorkspaceMembership,
            User,
            Organization,
            OrganizationMembership,
        ) = self._models()

        superuser = User.objects.create(email="super@example.com", is_superuser=True)
        ws_admin = User.objects.create(email="admin@example.com")
        ws_viewer = User.objects.create(email="viewer@example.com")

        active_ws = self._create_workspace(Workspace, "Active WS", "active-ws")
        archived_ws = self._create_workspace(
            Workspace, "Archived WS", "archived-ws", archived=True
        )

        WorkspaceMembership.objects.create(
            user=ws_admin,
            workspace=active_ws,
            role="ADMIN",
            notebooks_server_hash="h1",
            access_token="t1",
        )
        WorkspaceMembership.objects.create(
            user=ws_viewer,
            workspace=active_ws,
            role="VIEWER",
            notebooks_server_hash="h2",
            access_token="t2",
        )
        WorkspaceMembership.objects.create(
            user=ws_admin,
            workspace=archived_ws,
            role="ADMIN",
            notebooks_server_hash="h3",
            access_token="t3",
        )

        self.migrator.migrate(*self.migrate_to)

        Workspace = self.migrator.apps.get_model("workspaces", "Workspace")
        Organization = self.migrator.apps.get_model("user_management", "Organization")
        OrganizationMembership = self.migrator.apps.get_model(
            "user_management", "OrganizationMembership"
        )

        org = Organization.objects.get(name="Default Organization")
        self.assertEqual(org.slug, "default-organization")
        self.assertEqual(org.organization_type, "CORPORATE")

        self.assertEqual(
            Workspace.objects.get(slug="active-ws").organization_id, org.id
        )
        self.assertEqual(
            Workspace.objects.get(slug="archived-ws").organization_id, org.id
        )

        self.assertEqual(
            OrganizationMembership.objects.get(
                organization=org, user_id=superuser.id
            ).role,
            "owner",
        )
        self.assertEqual(
            OrganizationMembership.objects.get(
                organization=org, user_id=ws_admin.id
            ).role,
            "member",
        )
        self.assertFalse(
            OrganizationMembership.objects.filter(
                organization=org, user_id=ws_viewer.id
            ).exists()
        )

    def test_no_organization_created_without_orphans(self):
        """Fresh installs have no orphan workspaces, so the migration creates no
        organization — the first one is created later by an admin.
        """
        _, _, User, _, _ = self._models()
        User.objects.create(email="super@example.com", is_superuser=True)

        self.migrator.migrate(*self.migrate_to)

        Organization = self.migrator.apps.get_model("user_management", "Organization")
        self.assertFalse(Organization.objects.exists())

    @patch("hexa.user_management.models.get_forgejo_client")
    def test_raises_when_no_free_default_name_after_max_attempts(self, mock_get_client):
        """When every candidate default name is taken, the migration fails loudly
        instead of looping forever.
        """
        Workspace, _, _, _, _ = self._models()
        # Occupy the base name plus every suffix the loop would try (2..10),
        # matching MAX_NAME_ATTEMPTS in the migration.
        taken = ["Default Organization"] + [
            f"Default Organization {i}" for i in range(2, 11)
        ]
        for name in taken:
            RealOrganization.objects.create(
                name=name, organization_type=OrganizationType.CORPORATE
            )
        self._create_workspace(Workspace, "Orphan WS", "orphan-ws")

        with self.assertRaisesRegex(RuntimeError, "Could not find a free name"):
            self.migrator.migrate(*self.migrate_to)
