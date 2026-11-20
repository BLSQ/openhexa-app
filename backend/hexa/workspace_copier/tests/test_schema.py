from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.oauth.scopes import WORKSPACE_COPY_SCOPE
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspace_copier.models import WorkspaceCopyJob, WorkspaceCopyRun
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

DUPLICATE = """
mutation duplicate($input: DuplicateWorkspaceInput!) {
  duplicateWorkspace(input: $input) {
    success
    errors
    run { id status }
  }
}
"""

COPY_RUN = """
query run($id: UUID!) {
  workspaceCopyRun(id: $id) {
    id
    status
    logs
    error
    workspace { slug }
  }
}
"""

PERMISSIONS = """
query ws($slug: String!) {
  workspace(slug: $slug) { permissions { duplicate } }
}
"""


class DuplicateWorkspaceTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ROOT = User.objects.create_user(
            "root@bluesquarehub.com", "password", is_superuser=True
        )
        cls.ORGANIZATION = Organization.objects.create(name="Org")
        cls.WORKSPACE = create_workspace(
            cls.ROOT, name="Source", organization=cls.ORGANIZATION
        )

        cls.EDITOR = cls._org_user("editor@bluesquarehub.com")
        cls.VIEWER = cls._org_user("viewer@bluesquarehub.com")
        cls.OUTSIDER = cls._org_user("outsider@bluesquarehub.com")
        cls.ORG_ADMIN = cls._org_user(
            "admin@bluesquarehub.com", OrganizationMembershipRole.ADMIN
        )
        for user, role in (
            (cls.EDITOR, WorkspaceMembershipRole.EDITOR),
            (cls.VIEWER, WorkspaceMembershipRole.VIEWER),
        ):
            WorkspaceMembership.objects.create(
                user=user, workspace=cls.WORKSPACE, role=role
            )

    @classmethod
    def _org_user(cls, email, role=OrganizationMembershipRole.MEMBER):
        user = User.objects.create_user(email, "password")
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION, user=user, role=role
        )
        return user

    def duplicate(self, user, **overrides):
        self.client.force_login(user)
        variables = {
            "workspaceSlug": self.WORKSPACE.slug,
            "name": "Copy of Source",
            "resources": ["FILES", "CONNECTIONS"],
            "includeConnectionSecrets": False,
        }
        variables.update(overrides)
        return self.run_query(DUPLICATE, {"input": variables})["data"][
            "duplicateWorkspace"
        ]

    def test_an_editor_queues_a_same_server_copy_acting_as_themselves(self):
        result = self.duplicate(self.EDITOR)

        self.assertTrue(result["success"])
        self.assertEqual("QUEUED", result["run"]["status"])
        run = WorkspaceCopyRun.objects.get(id=result["run"]["id"])
        self.assertEqual(self.EDITOR, run.created_by)
        self.assertEqual(self.WORKSPACE.slug, run.source_slug)
        self.assertEqual(str(self.ORGANIZATION.id), run.target_organization_id)
        self.assertEqual("Copy of Source", run.target_workspace_name)
        self.assertEqual(["connections", "files"], run.resources)
        self.assertFalse(run.include_connection_secrets)
        self.assertTrue(run.same_server)
        self.assertIsNone(run.target_countries)
        self.assertIsNone(run.source_token)
        self.assertEqual(self.EDITOR, run.access_token.user)
        self.assertEqual(WORKSPACE_COPY_SCOPE, run.access_token.scope)
        self.assertTrue(
            WorkspaceCopyJob.objects.filter(args__run_id=str(run.id)).exists()
        )

    def test_an_organization_admin_can_duplicate_without_being_a_member(self):
        self.assertTrue(self.duplicate(self.ORG_ADMIN)["success"])

    def test_a_viewer_cannot_duplicate(self):
        result = self.duplicate(self.VIEWER)

        self.assertEqual(["PERMISSION_DENIED"], result["errors"])
        self.assertFalse(WorkspaceCopyRun.objects.exists())

    def test_a_member_of_the_organization_only_does_not_see_the_workspace(self):
        result = self.duplicate(self.OUTSIDER)

        self.assertEqual(["WORKSPACE_NOT_FOUND"], result["errors"])

    def test_an_organization_preventing_creation_blocks_duplication(self):
        FeatureFlag.objects.create(
            feature=Feature.objects.get_or_create(code="workspaces.prevent_create")[0],
            user=self.EDITOR,
        )

        self.assertEqual(["PERMISSION_DENIED"], self.duplicate(self.EDITOR)["errors"])

    @patch.object(Organization, "is_workspaces_limit_reached", return_value=True)
    def test_the_organization_workspaces_limit_is_enforced_up_front(self, _):
        result = self.duplicate(self.EDITOR)

        self.assertEqual(["WORKSPACES_LIMIT_REACHED"], result["errors"])
        self.assertFalse(WorkspaceCopyRun.objects.exists())

    def test_countries_override_the_source_ones(self):
        result = self.duplicate(self.EDITOR, countries=[{"code": "BE"}, {"code": "FR"}])

        run = WorkspaceCopyRun.objects.get(id=result["run"]["id"])
        self.assertEqual(["BE", "FR"], run.target_countries)

    def test_an_unknown_country_is_refused_before_queueing(self):
        result = self.duplicate(self.EDITOR, countries=[{"code": "ZZ"}])

        self.assertEqual(["INVALID_COUNTRY"], result["errors"])
        self.assertFalse(WorkspaceCopyRun.objects.exists())

    def test_permissions_duplicate(self):
        for user, expected in (
            (self.EDITOR, True),
            (self.ORG_ADMIN, True),
            (self.VIEWER, False),
        ):
            with self.subTest(user=user.email):
                self.client.force_login(user)
                data = self.run_query(PERMISSIONS, {"slug": self.WORKSPACE.slug})
                self.assertEqual(
                    expected, data["data"]["workspace"]["permissions"]["duplicate"]
                )


class WorkspaceCopyRunQueryTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.OWNER = User.objects.create_user("owner@bluesquarehub.com", "password")
        cls.OTHER = User.objects.create_user("other@bluesquarehub.com", "password")
        root = User.objects.create_user(
            "root@bluesquarehub.com", "password", is_superuser=True
        )
        cls.WORKSPACE = create_workspace(root, name="Copy")
        WorkspaceMembership.objects.create(
            user=cls.OWNER, workspace=cls.WORKSPACE, role=WorkspaceMembershipRole.ADMIN
        )
        cls.RUN = WorkspaceCopyRun.objects.create(
            created_by=cls.OWNER,
            source_slug="source",
            logs="10:00:00 => Copying files ...\n",
            result_workspace_slug=cls.WORKSPACE.slug,
        )

    def test_the_requester_follows_their_run(self):
        self.client.force_login(self.OWNER)

        run = self.run_query(COPY_RUN, {"id": str(self.RUN.id)})["data"][
            "workspaceCopyRun"
        ]

        self.assertEqual("QUEUED", run["status"])
        self.assertEqual("10:00:00 => Copying files ...\n", run["logs"])
        self.assertIsNone(run["error"])
        self.assertEqual(self.WORKSPACE.slug, run["workspace"]["slug"])

    def test_nobody_else_sees_it(self):
        self.client.force_login(self.OTHER)

        data = self.run_query(COPY_RUN, {"id": str(self.RUN.id)})

        self.assertIsNone(data["data"]["workspaceCopyRun"])

    def test_the_workspace_is_null_until_created(self):
        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(result_workspace_slug="")
        self.client.force_login(self.OWNER)

        run = self.run_query(COPY_RUN, {"id": str(self.RUN.id)})["data"][
            "workspaceCopyRun"
        ]

        self.assertIsNone(run["workspace"])
