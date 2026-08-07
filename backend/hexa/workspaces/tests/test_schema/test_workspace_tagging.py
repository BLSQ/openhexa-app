from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.tags.models import Tag
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

SET_TAGS_MUTATION = """
    mutation setWorkspaceTags($input: SetWorkspaceTagsInput!) {
        setWorkspaceTags(input: $input) {
            success
            errors
            workspace {
                tags {
                    name
                }
            }
        }
    }
"""

WORKSPACES_QUERY = """
    query workspaces($organizationId: UUID, $tags: [String!]) {
        workspaces(organizationId: $organizationId, tags: $tags) {
            totalItems
            items {
                slug
            }
        }
    }
"""


class WorkspaceTaggingTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_OWNER = User.objects.create_user("owner@bluesquarehub.com", "password")
        cls.USER_ADMIN = User.objects.create_user("admin@bluesquarehub.com", "password")
        # Workspace admin, but only a plain member of the organization
        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "wsadmin@bluesquarehub.com", "password"
        )
        cls.USER_OTHER_ORG_ADMIN = User.objects.create_user(
            "otherorg@bluesquarehub.com", "password"
        )

        cls.ORGANIZATION = Organization.objects.create(name="Bluesquare")
        cls.OTHER_ORGANIZATION = Organization.objects.create(name="Other Organization")

        for user, role in [
            (cls.USER_OWNER, OrganizationMembershipRole.OWNER),
            (cls.USER_ADMIN, OrganizationMembershipRole.ADMIN),
            (cls.USER_WORKSPACE_ADMIN, OrganizationMembershipRole.MEMBER),
        ]:
            OrganizationMembership.objects.create(
                organization=cls.ORGANIZATION, user=user, role=role
            )
        OrganizationMembership.objects.create(
            organization=cls.OTHER_ORGANIZATION,
            user=cls.USER_OTHER_ORG_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )

        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Senegal Workspace",
                organization=cls.ORGANIZATION,
            )
            cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Burundi Workspace",
                organization=cls.ORGANIZATION,
            )
            cls.OTHER_WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_OTHER_ORG_ADMIN,
                name="Foreign Workspace",
                organization=cls.OTHER_ORGANIZATION,
            )

        WorkspaceMembership.objects.create(
            user=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def set_tags(self, slug, tags):
        return self.run_query(
            SET_TAGS_MUTATION, {"input": {"slug": slug, "tags": tags}}
        )["data"]["setWorkspaceTags"]

    def test_organization_admin_sets_tags(self):
        self.client.force_login(self.USER_ADMIN)
        result = self.set_tags(self.WORKSPACE.slug, ["malaria", "project-x"])

        self.assertTrue(result["success"])
        self.assertEqual([], result["errors"])
        self.assertEqual(
            [{"name": "malaria"}, {"name": "project-x"}], result["workspace"]["tags"]
        )

    def test_organization_owner_sets_tags(self):
        self.client.force_login(self.USER_OWNER)
        result = self.set_tags(self.WORKSPACE.slug, ["malaria"])

        self.assertTrue(result["success"])
        self.assertEqual([{"name": "malaria"}], result["workspace"]["tags"])

    def test_workspace_admin_cannot_set_tags(self):
        """Tags are an organization-level taxonomy: workspace admins are excluded."""
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        result = self.set_tags(self.WORKSPACE.slug, ["malaria"])

        self.assertFalse(result["success"])
        self.assertEqual(["PERMISSION_DENIED"], result["errors"])
        self.assertEqual(0, self.WORKSPACE.tags.count())

    def test_set_tags_on_invisible_workspace(self):
        self.client.force_login(self.USER_ADMIN)
        result = self.set_tags(self.OTHER_WORKSPACE.slug, ["malaria"])

        self.assertFalse(result["success"])
        self.assertEqual(["NOT_FOUND"], result["errors"])

    def test_free_text_is_slugified(self):
        self.client.force_login(self.USER_ADMIN)
        result = self.set_tags(
            self.WORKSPACE.slug, ["Projet Côte d'Ivoire", "PMI 2026"]
        )

        self.assertTrue(result["success"])
        self.assertEqual(
            [{"name": "pmi-2026"}, {"name": "projet-cote-d-ivoire"}],
            result["workspace"]["tags"],
        )

    def test_unslugifiable_tag_is_rejected(self):
        self.client.force_login(self.USER_ADMIN)
        result = self.set_tags(self.WORKSPACE.slug, ["!!!"])

        self.assertFalse(result["success"])
        self.assertEqual(["INVALID_TAG"], result["errors"])
        self.assertEqual(0, self.WORKSPACE.tags.count())

    def test_set_tags_replaces_existing_ones(self):
        self.client.force_login(self.USER_ADMIN)
        self.set_tags(self.WORKSPACE.slug, ["malaria", "project-x"])
        result = self.set_tags(self.WORKSPACE.slug, ["project-y"])

        self.assertTrue(result["success"])
        self.assertEqual([{"name": "project-y"}], result["workspace"]["tags"])

    def test_empty_list_clears_tags(self):
        self.client.force_login(self.USER_ADMIN)
        self.set_tags(self.WORKSPACE.slug, ["malaria"])
        result = self.set_tags(self.WORKSPACE.slug, [])

        self.assertTrue(result["success"])
        self.assertEqual([], result["workspace"]["tags"])
        self.assertEqual(0, self.WORKSPACE.tags.count())

    def test_duplicate_names_are_collapsed(self):
        self.client.force_login(self.USER_ADMIN)
        result = self.set_tags(self.WORKSPACE.slug, ["Malaria", "malaria"])

        self.assertTrue(result["success"])
        self.assertEqual([{"name": "malaria"}], result["workspace"]["tags"])

    def test_filter_workspaces_by_tag(self):
        self.client.force_login(self.USER_ADMIN)
        self.set_tags(self.WORKSPACE.slug, ["malaria"])
        self.set_tags(self.WORKSPACE_2.slug, ["project-x"])

        result = self.run_query(
            WORKSPACES_QUERY,
            {"organizationId": str(self.ORGANIZATION.id), "tags": ["malaria"]},
        )["data"]["workspaces"]

        self.assertEqual(1, result["totalItems"])
        self.assertEqual([{"slug": self.WORKSPACE.slug}], result["items"])

    def test_filter_workspaces_by_several_tags_is_a_union(self):
        self.client.force_login(self.USER_ADMIN)
        self.set_tags(self.WORKSPACE.slug, ["malaria"])
        self.set_tags(self.WORKSPACE_2.slug, ["project-x"])

        result = self.run_query(
            WORKSPACES_QUERY,
            {
                "organizationId": str(self.ORGANIZATION.id),
                "tags": ["malaria", "project-x"],
            },
        )["data"]["workspaces"]

        self.assertEqual(2, result["totalItems"])

    def test_filter_by_unknown_tag_returns_nothing(self):
        self.client.force_login(self.USER_ADMIN)
        self.set_tags(self.WORKSPACE.slug, ["malaria"])

        result = self.run_query(
            WORKSPACES_QUERY,
            {"organizationId": str(self.ORGANIZATION.id), "tags": ["does-not-exist"]},
        )["data"]["workspaces"]

        self.assertEqual(0, result["totalItems"])

    def test_organization_workspace_tags_are_scoped(self):
        """Tag rows are shared across organizations, but the vocabulary is not."""
        self.client.force_login(self.USER_ADMIN)
        self.set_tags(self.WORKSPACE.slug, ["malaria", "project-x"])
        self.client.force_login(self.USER_OTHER_ORG_ADMIN)
        self.set_tags(self.OTHER_WORKSPACE.slug, ["malaria", "project-y"])

        self.assertEqual(1, Tag.objects.filter(name="malaria").count())

        query = """
            query organization($id: UUID!) {
                organization(id: $id) {
                    workspaceTags
                }
            }
        """
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(query, {"id": str(self.ORGANIZATION.id)})
        self.assertEqual(
            ["malaria", "project-x"], r["data"]["organization"]["workspaceTags"]
        )

        self.client.force_login(self.USER_OTHER_ORG_ADMIN)
        r = self.run_query(query, {"id": str(self.OTHER_ORGANIZATION.id)})
        self.assertEqual(
            ["malaria", "project-y"], r["data"]["organization"]["workspaceTags"]
        )

    def test_manage_tags_permission(self):
        query = """
            query workspace($slug: String!) {
                workspace(slug: $slug) {
                    permissions {
                        manageTags
                    }
                }
            }
        """
        for user, expected in [
            (self.USER_OWNER, True),
            (self.USER_ADMIN, True),
            (self.USER_WORKSPACE_ADMIN, False),
        ]:
            with self.subTest(user=user.email):
                self.client.force_login(user)
                r = self.run_query(query, {"slug": self.WORKSPACE.slug})
                self.assertEqual(
                    expected, r["data"]["workspace"]["permissions"]["manageTags"]
                )
