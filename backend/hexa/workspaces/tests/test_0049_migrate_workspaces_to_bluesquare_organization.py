from unittest.mock import patch

from django.test import TestCase

from hexa.core.test.migrator import Migrator


class Migration0049Test(TestCase):
    def setUp(self):
        self.migrator = Migrator()
        # First migrate user_management to have the user migration ready
        self.migrator.migrate(
            "user_management", "0028_migrate_users_to_bluesquare_organization"
        )
        # Then migrate workspaces to just before our target migration
        self.migrator.migrate("workspaces", "0048_workspace_organization")

    def get_organization_model(self):
        return self.migrator.apps.get_model("user_management", "Organization")

    def get_workspace_model(self):
        return self.migrator.apps.get_model("workspaces", "Workspace")

    def test_migrate_workspaces_with_existing_organization(self):
        """Test that workspaces are assigned to existing Bluesquare organization"""
        Organization = self.get_organization_model()
        Workspace = self.get_workspace_model()

        organization = Organization.objects.create(
            name="Bluesquare",
            organization_type="CORPORATE",
            short_name="bluesquare",
            description="Test organization",
        )

        workspace1 = Workspace.objects.create(
            name="Workspace 1", slug="workspace-1", db_name="ws1_db"
        )
        workspace2 = Workspace.objects.create(
            name="Workspace 2",
            slug="workspace-2",
            organization=organization,
            db_name="ws2_db",
        )
        workspace3 = Workspace.objects.create(
            name="Workspace 3", slug="workspace-3", db_name="ws3_db"
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "workspaces", "0049_migrate_workspaces_to_bluesquare_organization"
            )

        workspace1.refresh_from_db()
        workspace3.refresh_from_db()

        self.assertEqual(workspace1.organization, organization)
        self.assertEqual(workspace2.organization, organization)  # Already assigned
        self.assertEqual(workspace3.organization, organization)

        mock_print.assert_called_with(
            "Assigned 2 workspaces to Bluesquare organization"
        )

    def test_migrate_workspaces_no_organization(self):
        """Test that migration skips when Bluesquare organization doesn't exist"""
        Workspace = self.get_workspace_model()

        workspace = Workspace.objects.create(
            name="Workspace", slug="workspace", db_name="test_db"
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "workspaces", "0049_migrate_workspaces_to_bluesquare_organization"
            )

        workspace.refresh_from_db()
        self.assertIsNone(workspace.organization)
        mock_print.assert_called_with(
            "Bluesquare organization not found, skipping workspace migration"
        )

    def test_migrate_workspaces_all_assigned(self):
        """Test when all workspaces already have organization assigned"""
        Organization = self.get_organization_model()
        Workspace = self.get_workspace_model()

        organization = Organization.objects.create(
            name="Bluesquare",
            organization_type="CORPORATE",
            short_name="bluesquare",
            description="Test organization",
        )

        Workspace.objects.create(
            name="Workspace",
            slug="workspace",
            organization=organization,
            db_name="assigned_db",
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "workspaces", "0049_migrate_workspaces_to_bluesquare_organization"
            )

        self.assertEqual(Workspace.objects.filter(organization=organization).count(), 1)
        mock_print.assert_called_with(
            "All workspaces already have an organization assigned"
        )

    def test_migrate_workspaces_empty_database(self):
        """Test migration with no workspaces"""
        Organization = self.get_organization_model()
        Workspace = self.get_workspace_model()

        Organization.objects.create(
            name="Bluesquare",
            organization_type="CORPORATE",
            short_name="bluesquare",
            description="Test organization",
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "workspaces", "0049_migrate_workspaces_to_bluesquare_organization"
            )

        self.assertEqual(Workspace.objects.count(), 0)
        mock_print.assert_called_with(
            "All workspaces already have an organization assigned"
        )
