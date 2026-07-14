from unittest.mock import patch

from django.test import TransactionTestCase

from hexa.core.test.migrator import Migrator
from hexa.user_management.models import Organization as RealOrganization
from hexa.user_management.models import (
    OrganizationMembership as RealOrganizationMembership,
)
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

    def test_default_organization_created_when_none_exists(self):
        """Fresh installs (no orphan workspaces and no organization) still get a
        default organization so workspaces can be created, owned by superusers.
        """
        _, _, User, Organization, _ = self._models()
        superuser = User.objects.create(email="super@example.com", is_superuser=True)

        self.migrator.migrate(*self.migrate_to)

        Organization = self.migrator.apps.get_model("user_management", "Organization")
        OrganizationMembership = self.migrator.apps.get_model(
            "user_management", "OrganizationMembership"
        )

        org = Organization.objects.get(name="Default Organization")
        self.assertEqual(org.organization_type, "CORPORATE")
        self.assertEqual(
            OrganizationMembership.objects.get(
                organization=org, user_id=superuser.id
            ).role,
            "owner",
        )

    @patch("hexa.user_management.models.get_forgejo_client")
    def test_no_default_organization_created_when_one_already_exists(
        self, mock_get_client
    ):
        # The Migrator only rewinds the workspaces app, so the user_management
        # table keeps its HEAD schema (slug is NOT NULL). Insert through the real
        # model, which populates the slug, rather than the historical one.
        RealOrganization.objects.create(
            name="Existing Organization",
            organization_type=OrganizationType.CORPORATE,
        )

        self.migrator.migrate(*self.migrate_to)

        Organization = self.migrator.apps.get_model("user_management", "Organization")
        self.assertFalse(
            Organization.objects.filter(name="Default Organization").exists()
        )
        self.assertEqual(Organization.objects.count(), 1)

    def test_reverse_keeps_default_organization_that_has_workspaces(self):
        """Rolling back must not delete a default organization that is in use."""
        Workspace, _, _, _, _ = self._models()
        self._create_workspace(Workspace, "Active WS", "active-ws")

        self.migrator.migrate(*self.migrate_to)
        Organization = self.migrator.apps.get_model("user_management", "Organization")
        self.assertTrue(
            Organization.objects.filter(name="Default Organization").exists()
        )

        self.migrator.migrate(*self.migrate_from)
        Organization = self.migrator.apps.get_model("user_management", "Organization")
        self.assertTrue(
            Organization.objects.filter(name="Default Organization").exists()
        )

    def test_reverse_removes_empty_default_organization(self):
        """Rolling back removes the auto-created default org (and its memberships)
        when it owns no workspaces.
        """
        _, _, User, _, _ = self._models()
        User.objects.create(email="super@example.com", is_superuser=True)

        self.migrator.migrate(*self.migrate_to)
        Organization = self.migrator.apps.get_model("user_management", "Organization")
        OrganizationMembership = self.migrator.apps.get_model(
            "user_management", "OrganizationMembership"
        )
        org = Organization.objects.get(name="Default Organization")
        self.assertTrue(
            OrganizationMembership.objects.filter(organization=org).exists()
        )

        self.migrator.migrate(*self.migrate_from)
        Organization = self.migrator.apps.get_model("user_management", "Organization")
        OrganizationMembership = self.migrator.apps.get_model(
            "user_management", "OrganizationMembership"
        )
        self.assertFalse(
            Organization.objects.filter(name="Default Organization").exists()
        )
        self.assertFalse(
            OrganizationMembership.objects.filter(organization_id=org.id).exists()
        )

    @patch("hexa.user_management.models.get_forgejo_client")
    def test_orphans_reuse_existing_default_organization(self, mock_get_client):
        """When a default organization already exists, orphans are attached to it
        instead of creating a duplicate, and existing memberships don't clash.
        """
        Workspace, _, User, _, _ = self._models()
        superuser = User.objects.create(email="super@example.com", is_superuser=True)
        existing = RealOrganization.objects.create(
            name="Default Organization",
            organization_type=OrganizationType.CORPORATE,
        )
        RealOrganizationMembership.objects.create(
            organization=existing, user_id=superuser.id, role="owner"
        )
        self._create_workspace(Workspace, "Orphan WS", "orphan-ws")

        self.migrator.migrate(*self.migrate_to)

        Workspace = self.migrator.apps.get_model("workspaces", "Workspace")
        Organization = self.migrator.apps.get_model("user_management", "Organization")
        OrganizationMembership = self.migrator.apps.get_model(
            "user_management", "OrganizationMembership"
        )

        self.assertEqual(
            Organization.objects.filter(name="Default Organization").count(), 1
        )
        self.assertEqual(
            Workspace.objects.get(slug="orphan-ws").organization_id, existing.id
        )
        self.assertEqual(
            OrganizationMembership.objects.filter(
                organization_id=existing.id, user_id=superuser.id
            ).count(),
            1,
        )
