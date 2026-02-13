from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

from hexa.core.test import TestCase
from hexa.superset.models import SupersetDashboard, SupersetInstance
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import SupersetWebapp, Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.user_admin = User.objects.create_user(
            "admin@bluesquarehub.com",
            "admin",
        )
        WorkspaceMembership.objects.create(
            user=self.user_admin,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.user_viewer = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "foopassword",
        )
        WorkspaceMembership.objects.create(
            user=self.user_viewer,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )
        self.user_editor = User.objects.create_user(
            "editor@bluesquarehub.com",
            "foopassword",
        )
        WorkspaceMembership.objects.create(
            user=self.user_editor,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.EDITOR,
        )
        self.webapp = Webapp.objects.create(
            name="Test Webapp",
            slug="test-webapp",
            description="A test webapp",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )

    def test_webapp_creation(self):
        self.assertEqual(self.webapp.name, "Test Webapp")
        self.assertEqual(self.webapp.description, "A test webapp")
        self.assertEqual(self.webapp.workspace, self.workspace)
        self.assertEqual(self.webapp.created_by, self.user_admin)
        self.assertEqual(self.webapp.url, "https://example.com")

    def test_webapp_str(self):
        self.assertEqual(str(self.webapp), "Test Webapp")

    def test_webapp_update(self):
        self.webapp.name = "Updated Webapp"
        self.webapp.save()
        self.assertEqual(self.webapp.name, "Updated Webapp")

    def test_webapp_soft_delete(self):
        webapp_id = self.webapp.id
        self.webapp.delete()
        self.assertFalse(Webapp.objects.filter(id=webapp_id).exists())
        self.assertTrue(Webapp.all_objects.get(id=webapp_id).is_deleted)

    def test_is_favorite(self):
        self.assertFalse(self.webapp.is_favorite(self.user_viewer))
        self.webapp.add_to_favorites(self.user_viewer)
        self.assertTrue(self.webapp.is_favorite(self.user_viewer))

    def test_add_to_favorites(self):
        self.webapp.add_to_favorites(self.user_viewer)
        self.assertIn(self.user_viewer, self.webapp.favorites.all())

    def test_remove_from_favorites(self):
        self.webapp.add_to_favorites(self.user_viewer)
        self.webapp.remove_from_favorites(self.user_viewer)
        self.assertNotIn(self.user_viewer, self.webapp.favorites.all())

    def test_create_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            Webapp.objects.create_if_has_perm(
                self.user_viewer,
                self.workspace,
                name="New Webapp",
                workspace=self.workspace,
                created_by=self.user_viewer,
                url="https://example.com",
            )

        webapp = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="New Webapp1",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )
        self.assertTrue(Webapp.objects.filter(id=webapp.id).exists())

        webapp = Webapp.objects.create_if_has_perm(
            self.user_editor,
            self.workspace,
            name="New Webapp2",
            workspace=self.workspace,
            created_by=self.user_editor,
            url="https://example.com",
        )
        self.assertTrue(Webapp.objects.filter(id=webapp.id).exists())

    def test_update_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            Webapp.objects.update_if_has_perm(
                self.user_viewer, self.webapp, name="Updated Webapp"
            )

        webapp = Webapp.objects.update_if_has_perm(
            self.user_admin, self.webapp, name="Updated Webapp by admin"
        )
        self.assertEqual(webapp.name, "Updated Webapp by admin")

        webapp = Webapp.objects.update_if_has_perm(
            self.user_editor, self.webapp, name="Updated Webapp by editor"
        )
        self.assertEqual(webapp.name, "Updated Webapp by editor")

    def test_delete_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            Webapp.objects.delete_if_has_perm(self.user_viewer, self.webapp)

        with self.assertRaises(PermissionDenied):
            Webapp.objects.delete_if_has_perm(self.user_editor, self.webapp)

        Webapp.objects.delete_if_has_perm(self.user_admin, self.webapp)
        self.assertFalse(Webapp.objects.filter(id=self.webapp.id).exists())
        self.assertTrue(Webapp.all_objects.get(id=self.webapp.id).is_deleted)

    def test_webapp_slug_auto_generation(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="My Test Webapp",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )
        self.assertEqual(webapp.slug, "my-test-webapp")

    def test_webapp_slug_collision_handling(self):
        from hexa.webapps.models import create_webapp_slug

        webapp1 = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="Collision Test",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )
        self.assertEqual(webapp1.slug, "collision-test")

        slug2 = create_webapp_slug("Collision Test", self.workspace)

        self.assertNotEqual(slug2, "collision-test")
        self.assertTrue(slug2.startswith("collision-test-"))
        self.assertEqual(len(slug2), len("collision-test-") + 6)

    def test_webapp_slug_uniqueness_per_workspace(self):
        workspace2 = Workspace.objects.create_if_has_perm(
            self.user_admin,
            name="Test Workspace 2",
            description="Second test workspace",
            countries=[{"code": "FR"}],
        )

        webapp1 = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="Unique Webapp",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )

        webapp2 = Webapp.objects.create_if_has_perm(
            self.user_admin,
            workspace2,
            name="Unique Webapp",
            workspace=workspace2,
            created_by=self.user_admin,
            url="https://example.com",
        )

        self.assertEqual(webapp1.slug, "unique-webapp")
        self.assertEqual(webapp2.slug, "unique-webapp")
        self.assertNotEqual(webapp1.workspace, webapp2.workspace)

    def test_webapp_slug_read_only(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="Original Name",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )
        original_slug = webapp.slug

        webapp.name = "New Name"
        webapp.save()

        self.assertEqual(webapp.slug, original_slug)

    def test_webapp_slug_in_shortcut_url(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="Shortcut Test",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )
        shortcut = webapp.to_shortcut_item()
        expected_url = f"/workspaces/{self.workspace.slug}/webapps/{webapp.slug}/play"
        self.assertEqual(shortcut["url"], expected_url)
        self.assertIn(webapp.slug, shortcut["url"])
        self.assertNotIn(str(webapp.id), shortcut["url"])

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Webapp.objects.create(
                name=self.webapp.name,
                slug=self.webapp.slug,
                workspace=self.webapp.workspace,
                created_by=self.user_admin,
                url="https://example.com",
            )


class WebappOrganizationAdminOwnerPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-webapp",
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
        cls.NON_ORG_USER = User.objects.create_user(
            "nonorg@bluesquarehub.com", "password"
        )

        cls.WORKSPACE_ADMIN = User.objects.create_user(
            "workspace_admin@bluesquarehub.com", "password", is_superuser=True
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

        cls.WORKSPACE_1 = Workspace.objects.create_if_has_perm(
            cls.WORKSPACE_ADMIN,
            name="Workspace 1",
            description="First workspace in organization",
            organization=cls.ORGANIZATION,
        )

        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.WORKSPACE_ADMIN,
            name="Workspace 2",
            description="Second workspace in organization",
            organization=cls.ORGANIZATION,
        )

        cls.WORKSPACE_ADMIN.is_superuser = False
        cls.WORKSPACE_ADMIN.save()

        cls.WEBAPP_1 = Webapp.objects.create(
            workspace=cls.WORKSPACE_1,
            name="Webapp in workspace 1",
            slug="webapp-in-workspace-1",
            description="Webapp in workspace where org admin/owner is not a member",
            created_by=cls.WORKSPACE_ADMIN,
            url="https://example1.com",
        )

        cls.WEBAPP_2 = Webapp.objects.create(
            workspace=cls.WORKSPACE_2,
            name="Webapp in workspace 2",
            slug="webapp-in-workspace-2",
            description="Webapp in another workspace in same org",
            created_by=cls.WORKSPACE_ADMIN,
            url="https://example2.com",
        )

    def test_organization_owner_can_access_all_webapps_in_organization(self):
        webapps = Webapp.objects.filter_for_user(self.ORG_OWNER_USER)

        self.assertIn(self.WEBAPP_1, webapps)
        self.assertIn(self.WEBAPP_2, webapps)

    def test_organization_admin_can_access_all_webapps_in_organization(self):
        webapps = Webapp.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.WEBAPP_1, webapps)
        self.assertIn(self.WEBAPP_2, webapps)

    def test_organization_member_cannot_access_webapps_from_non_member_workspaces(
        self,
    ):
        webapps = Webapp.objects.filter_for_user(self.ORG_MEMBER_USER)

        self.assertNotIn(self.WEBAPP_1, webapps)
        self.assertNotIn(self.WEBAPP_2, webapps)

    def test_non_organization_member_cannot_access_organization_webapps(self):
        webapps = Webapp.objects.filter_for_user(self.NON_ORG_USER)

        self.assertNotIn(self.WEBAPP_1, webapps)
        self.assertNotIn(self.WEBAPP_2, webapps)

    def test_organization_admin_owner_access_combined_with_workspace_membership(self):
        WorkspaceMembership.objects.create(
            workspace=self.WORKSPACE_1,
            user=self.ORG_ADMIN_USER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        webapps = Webapp.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.WEBAPP_1, webapps)
        self.assertIn(self.WEBAPP_2, webapps)

    def test_webapp_filter_favorites_with_org_admin_owner(self):
        self.WEBAPP_1.add_to_favorites(self.ORG_OWNER_USER)
        self.WEBAPP_2.add_to_favorites(self.ORG_ADMIN_USER)

        owner_favorites = Webapp.objects.filter_favorites(self.ORG_OWNER_USER)
        admin_favorites = Webapp.objects.filter_favorites(self.ORG_ADMIN_USER)
        member_favorites = Webapp.objects.filter_favorites(self.ORG_MEMBER_USER)

        self.assertIn(self.WEBAPP_1, owner_favorites)
        self.assertIn(self.WEBAPP_2, admin_favorites)
        self.assertEqual(member_favorites.count(), 0)


class SupersetWebappModelTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-superset",
        )
        self.superset_instance = SupersetInstance.objects.create(
            name="Superset",
            url="https://superset.example.com",
            api_username="test",
            api_password="password",
            organization=self.organization,
        )
        self.workspace = Workspace.objects.create(
            name="Test Workspace",
            organization=self.organization,
        )
        self.user_admin = User.objects.create_user(
            "admin@test.com",
            "admin",
        )
        WorkspaceMembership.objects.create(
            user=self.user_admin,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.user_viewer = User.objects.create_user(
            "viewer@test.com",
            "viewer",
        )
        WorkspaceMembership.objects.create(
            user=self.user_viewer,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_create_if_has_perm(self):
        webapp = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-123",
            name="My Dashboard",
            created_by=self.user_admin,
            description="A description",
        )

        self.assertEqual(webapp.name, "My Dashboard")
        self.assertEqual(webapp.type, Webapp.WebappType.SUPERSET)
        self.assertEqual(webapp.workspace, self.workspace)
        self.assertEqual(webapp.superset_dashboard.external_id, "ext-123")
        self.assertEqual(
            webapp.superset_dashboard.superset_instance, self.superset_instance
        )

    def test_create_if_has_perm_denied(self):
        with self.assertRaises(PermissionDenied):
            SupersetWebapp.create_if_has_perm(
                principal=self.user_viewer,
                workspace=self.workspace,
                superset_instance=self.superset_instance,
                external_dashboard_id="ext-123",
                name="My Dashboard",
                created_by=self.user_viewer,
            )

    def test_create_same_external_id_creates_separate_dashboards(self):
        webapp1 = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-123",
            name="Dashboard 1",
            created_by=self.user_admin,
        )
        webapp2 = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-123",
            name="Dashboard 2",
            created_by=self.user_admin,
        )

        self.assertNotEqual(
            webapp1.superset_dashboard.id, webapp2.superset_dashboard.id
        )
        self.assertEqual(
            webapp1.superset_dashboard.external_id,
            webapp2.superset_dashboard.external_id,
        )

    def test_delete_if_has_perm_deletes_dashboard(self):
        webapp = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-123",
            name="To Delete",
            created_by=self.user_admin,
        )
        dashboard_id = webapp.superset_dashboard.id
        webapp_id = webapp.id

        webapp.delete_if_has_perm(principal=self.user_admin)

        self.assertFalse(SupersetDashboard.objects.filter(id=dashboard_id).exists())
        self.assertFalse(Webapp.objects.filter(id=webapp_id).exists())

    def test_delete_if_has_perm_on_base_webapp_deletes_dashboard(self):
        superset_webapp = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-base-delete",
            name="Base Delete",
            created_by=self.user_admin,
        )
        dashboard_id = superset_webapp.superset_dashboard.id
        webapp_id = superset_webapp.id

        webapp = Webapp.objects.get(pk=webapp_id)
        webapp.delete_if_has_perm(principal=self.user_admin)

        self.assertFalse(SupersetDashboard.objects.filter(id=dashboard_id).exists())
        self.assertFalse(Webapp.objects.filter(id=webapp_id).exists())

    def test_delete_if_has_perm_denied(self):
        webapp = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-123",
            name="Protected",
            created_by=self.user_admin,
        )

        with self.assertRaises(PermissionDenied):
            webapp.delete_if_has_perm(principal=self.user_viewer)

        self.assertTrue(SupersetWebapp.objects.filter(id=webapp.id).exists())
        self.assertTrue(
            SupersetDashboard.objects.filter(id=webapp.superset_dashboard.id).exists()
        )

    def test_delete_does_not_affect_standalone_dashboards(self):
        standalone_dashboard = SupersetDashboard.objects.create(
            external_id="standalone-123",
            superset_instance=self.superset_instance,
            name="Standalone Dashboard",
        )
        webapp = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id=standalone_dashboard.external_id,
            name="Webapp Dashboard",
            created_by=self.user_admin,
        )

        webapp.delete_if_has_perm(principal=self.user_admin)

        self.assertTrue(
            SupersetDashboard.objects.filter(id=standalone_dashboard.id).exists()
        )

    def test_update_dashboard(self):
        webapp = SupersetWebapp.create_if_has_perm(
            principal=self.user_admin,
            workspace=self.workspace,
            superset_instance=self.superset_instance,
            external_dashboard_id="ext-123",
            name="Original",
            created_by=self.user_admin,
        )

        other_instance = SupersetInstance.objects.create(
            name="Other Superset",
            url="https://other-superset.example.com",
            api_username="other",
            api_password="password",
            organization=self.organization,
        )

        webapp.update_dashboard(other_instance, "ext-999")

        webapp.refresh_from_db()
        webapp.superset_dashboard.refresh_from_db()
        self.assertEqual(webapp.superset_dashboard.external_id, "ext-999")
        self.assertEqual(webapp.superset_dashboard.superset_instance, other_instance)
