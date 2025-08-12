from unittest.mock import patch

from django.test import TestCase

from hexa.core.test.migrator import Migrator


class Migration0028Test(TestCase):
    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(
            "user_management", "0027_alter_organizationinvitation_workspace_invitations"
        )

    def get_organization_model(self):
        return self.migrator.apps.get_model("user_management", "Organization")

    def get_user_model(self):
        return self.migrator.apps.get_model("user_management", "User")

    def get_organization_membership_model(self):
        return self.migrator.apps.get_model("user_management", "OrganizationMembership")

    def test_migrate_users_with_existing_organization(self):
        """Test that users are added to existing Bluesquare organization"""
        Organization = self.get_organization_model()
        User = self.get_user_model()
        OrganizationMembership = self.get_organization_membership_model()

        organization = Organization.objects.create(
            name="Bluesquare",
            organization_type="CORPORATE",
            short_name="bluesquare",
            description="Test organization",
        )

        user1 = User.objects.create(email="user1@example.com")
        user2 = User.objects.create(email="user2@example.com")

        # Add user1 to organization
        OrganizationMembership.objects.create(
            organization=organization, user=user1, role="member"
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "user_management", "0028_migrate_users_to_bluesquare_organization"
            )

        # Verify user2 was added to organization
        self.assertEqual(
            OrganizationMembership.objects.filter(organization=organization).count(), 2
        )

        user2_membership = OrganizationMembership.objects.get(
            organization=organization, user=user2
        )
        self.assertEqual(user2_membership.role, "member")

        mock_print.assert_called_with("Added 1 users to Bluesquare organization")

    def test_migrate_users_no_organization(self):
        """Test that migration skips when Bluesquare organization doesn't exist"""
        User = self.get_user_model()
        OrganizationMembership = self.get_organization_membership_model()

        User.objects.create(email="user3@example.com")

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "user_management", "0028_migrate_users_to_bluesquare_organization"
            )

        self.assertEqual(OrganizationMembership.objects.count(), 0)
        mock_print.assert_called_with(
            "Bluesquare organization not found, skipping user migration"
        )

    def test_migrate_users_all_users_already_members(self):
        """Test when all users are already organization members"""
        Organization = self.get_organization_model()
        User = self.get_user_model()
        OrganizationMembership = self.get_organization_membership_model()

        organization = Organization.objects.create(
            name="Bluesquare",
            organization_type="CORPORATE",
            short_name="bluesquare",
            description="Test organization",
        )

        user = User.objects.create(email="user4@example.com")
        OrganizationMembership.objects.create(
            organization=organization, user=user, role="member"
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "user_management", "0028_migrate_users_to_bluesquare_organization"
            )

        self.assertEqual(
            OrganizationMembership.objects.filter(organization=organization).count(), 1
        )
        mock_print.assert_called_with("No users needed to be added to organizations")

    def test_migrate_users_empty_database(self):
        """Test migration with no users"""
        Organization = self.get_organization_model()
        OrganizationMembership = self.get_organization_membership_model()

        Organization.objects.create(
            name="Bluesquare",
            organization_type="CORPORATE",
            short_name="bluesquare",
            description="Test organization",
        )

        with patch("builtins.print") as mock_print:
            self.migrator.migrate(
                "user_management", "0028_migrate_users_to_bluesquare_organization"
            )

        self.assertEqual(OrganizationMembership.objects.count(), 0)
        mock_print.assert_called_with("No users needed to be added to organizations")
