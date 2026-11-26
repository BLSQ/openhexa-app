from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspace_copier.models import (
    WorkspaceCopyJob,
    WorkspaceCopyRun,
    WorkspaceCopyRunStatus,
)
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
query run($id: UUID!, $offset: Int) {
  workspaceCopyRun(id: $id) {
    id
    status
    targetWorkspaceName
    sourceWorkspaceSlug
    sourceWorkspace { slug }
    logs(offset: $offset) { text nextOffset }
    steps { name status }
    warnings
    error
    workspace { slug }
  }
}
"""

ACTIVE_RUN = """
query { activeWorkspaceCopyRun { id } }
"""

DATABASE_IN_USE = """
query ws($slug: String!) {
  workspace(slug: $slug) { databaseInUse }
}
"""

PERMISSIONS = """
query ws($slug: String!) {
  workspace(slug: $slug) { permissions { duplicate } }
}
"""

ORGANIZATION_PERMISSIONS = """
query ws($organizationId: UUID!) {
  workspaces(organizationId: $organizationId) {
    items { permissions { duplicate } }
  }
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
        cls.WS_ADMIN = cls._org_user("ws-admin@bluesquarehub.com")
        cls.EXTERNAL_ADMIN = User.objects.create_user(
            "external@bluesquarehub.com", "password"
        )
        cls.VIEWER = cls._org_user("viewer@bluesquarehub.com")
        cls.OUTSIDER = cls._org_user("outsider@bluesquarehub.com")
        cls.ORG_ADMIN = cls._org_user(
            "admin@bluesquarehub.com", OrganizationMembershipRole.ADMIN
        )
        for user, role in (
            (cls.EDITOR, WorkspaceMembershipRole.EDITOR),
            (cls.VIEWER, WorkspaceMembershipRole.VIEWER),
            (cls.WS_ADMIN, WorkspaceMembershipRole.ADMIN),
            (cls.EXTERNAL_ADMIN, WorkspaceMembershipRole.ADMIN),
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
        self.assertTrue(run.acts_as_requester)
        # The worker issues the token when the run starts.
        self.assertIsNone(run.access_token)
        self.assertTrue(
            WorkspaceCopyJob.objects.filter(args__run_id=str(run.id)).exists()
        )

    def test_a_workspace_admin_queues_a_copy_acting_as_themselves(self):
        result = self.duplicate(self.WS_ADMIN)

        self.assertTrue(result["success"])
        run = WorkspaceCopyRun.objects.get(id=result["run"]["id"])
        self.assertEqual(self.WS_ADMIN, run.created_by)
        self.assertTrue(run.acts_as_requester)

    def test_an_external_collaborator_cannot_duplicate_even_as_workspace_admin(self):
        result = self.duplicate(self.EXTERNAL_ADMIN)

        self.assertEqual(["PERMISSION_DENIED"], result["errors"])
        self.assertFalse(WorkspaceCopyRun.objects.exists())

    def test_all_dataset_versions_is_off_unless_asked(self):
        default = self.duplicate(self.EDITOR)
        WorkspaceCopyRun.objects.update(status=WorkspaceCopyRunStatus.SUCCESS)
        every_version = self.duplicate(self.EDITOR, allDatasetVersions=True)

        self.assertFalse(
            WorkspaceCopyRun.objects.get(id=default["run"]["id"]).all_dataset_versions
        )
        self.assertTrue(
            WorkspaceCopyRun.objects.get(
                id=every_version["run"]["id"]
            ).all_dataset_versions
        )

    @patch("hexa.workspace_copier.duplicate.database_in_use", return_value=True)
    def test_a_database_in_use_is_refused_before_queueing(self, _):
        result = self.duplicate(self.EDITOR, resources=["FILES", "DATABASE"])

        self.assertEqual(["DATABASE_IN_USE"], result["errors"])
        self.assertFalse(WorkspaceCopyRun.objects.exists())

    @patch("hexa.workspace_copier.duplicate.database_in_use", return_value=True)
    def test_a_database_in_use_does_not_matter_when_not_copied(self, _):
        self.assertTrue(self.duplicate(self.EDITOR)["success"])

    @patch("hexa.workspace_copier.schema.types.database_in_use", return_value=True)
    def test_database_in_use_is_only_told_to_those_who_can_duplicate(self, _):
        for user, expected in ((self.EDITOR, True), (self.VIEWER, None)):
            with self.subTest(user=user.email):
                self.client.force_login(user)
                data = self.run_query(DATABASE_IN_USE, {"slug": self.WORKSPACE.slug})
                self.assertEqual(expected, data["data"]["workspace"]["databaseInUse"])

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

    def test_a_second_copy_waits_for_the_first_to_finish(self):
        first = self.duplicate(self.EDITOR)

        second = self.duplicate(self.EDITOR)

        self.assertEqual(["COPY_ALREADY_RUNNING"], second["errors"])
        self.assertEqual(1, WorkspaceCopyRun.objects.count())
        WorkspaceCopyRun.objects.filter(id=first["run"]["id"]).update(
            status=WorkspaceCopyRunStatus.SUCCESS
        )
        self.assertTrue(self.duplicate(self.EDITOR)["success"])

    def test_other_users_can_copy_while_one_is_running(self):
        self.duplicate(self.EDITOR)

        self.assertTrue(self.duplicate(self.ORG_ADMIN)["success"])

    def test_countries_override_the_source_ones(self):
        result = self.duplicate(self.EDITOR, countries=[{"code": "BE"}, {"code": "FR"}])

        run = WorkspaceCopyRun.objects.get(id=result["run"]["id"])
        self.assertEqual(["BE", "FR"], run.target_countries)

    def test_an_unknown_country_is_refused_before_queueing(self):
        result = self.duplicate(self.EDITOR, countries=[{"code": "ZZ"}])

        self.assertEqual(["INVALID_COUNTRY"], result["errors"])
        self.assertFalse(WorkspaceCopyRun.objects.exists())

    def test_a_blank_or_too_long_name_is_refused(self):
        for name in ("   ", "x" * 256):
            with self.subTest(name=name):
                result = self.duplicate(self.EDITOR, name=name)

                self.assertEqual(["INVALID_NAME"], result["errors"])
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

    def test_listing_workspaces_checks_the_organization_once(self):
        for name in ("Second", "Third"):
            workspace = create_workspace(
                self.ROOT, name=name, organization=self.ORGANIZATION
            )
            WorkspaceMembership.objects.create(
                user=self.EDITOR,
                workspace=workspace,
                role=WorkspaceMembershipRole.EDITOR,
            )
        self.client.force_login(self.EDITOR)

        with patch(
            "hexa.user_management.permissions.create_workspace", return_value=True
        ) as create_workspace_rule:
            data = self.run_query(
                ORGANIZATION_PERMISSIONS, {"organizationId": str(self.ORGANIZATION.id)}
            )

        items = data["data"]["workspaces"]["items"]
        self.assertEqual(3, len(items))
        self.assertTrue(all(item["permissions"]["duplicate"] for item in items))
        create_workspace_rule.assert_called_once()


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
            target_workspace_name="Copy",
            logs="10:00:00 => Copying files ...\n10:00:01 [1] copied a.csv\n",
            result_workspace_slug=cls.WORKSPACE.slug,
            acts_as_requester=True,
        )

    def query_run(self, user, offset=0):
        self.client.force_login(user)
        return self.run_query(COPY_RUN, {"id": str(self.RUN.id), "offset": offset})[
            "data"
        ]["workspaceCopyRun"]

    def test_the_requester_follows_their_run(self):
        run = self.query_run(self.OWNER)

        self.assertEqual("QUEUED", run["status"])
        self.assertEqual("Copy", run["targetWorkspaceName"])
        self.assertEqual("source", run["sourceWorkspaceSlug"])
        self.assertEqual(
            "10:00:00 => Copying files ...\n10:00:01 [1] copied a.csv\n",
            run["logs"]["text"],
        )
        self.assertIsNone(run["error"])
        self.assertEqual(self.WORKSPACE.slug, run["workspace"]["slug"])

    def test_logs_from_an_offset_return_only_newer_lines(self):
        first = self.query_run(self.OWNER)["logs"]
        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(
            logs=self.RUN.logs + "10:00:02 [2] copied b.csv\n"
        )

        newer = self.query_run(self.OWNER, offset=first["nextOffset"])["logs"]

        self.assertEqual("10:00:02 [2] copied b.csv\n", newer["text"])
        self.assertEqual(len(self.RUN.logs) + 26, newer["nextOffset"])
        caught_up = self.query_run(self.OWNER, offset=newer["nextOffset"])["logs"]
        self.assertEqual("", caught_up["text"])

    def test_the_active_run_is_found_until_it_finishes(self):
        self.client.force_login(self.OWNER)
        data = self.run_query(ACTIVE_RUN)["data"]["activeWorkspaceCopyRun"]
        self.assertEqual(str(self.RUN.id), data["id"])

        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(
            status=WorkspaceCopyRunStatus.FAILED
        )

        self.assertIsNone(self.run_query(ACTIVE_RUN)["data"]["activeWorkspaceCopyRun"])

    def test_another_users_active_run_is_not_theirs(self):
        self.client.force_login(self.OTHER)

        self.assertIsNone(self.run_query(ACTIVE_RUN)["data"]["activeWorkspaceCopyRun"])

    def test_nobody_else_sees_it(self):
        self.assertIsNone(self.query_run(self.OTHER))

    def test_the_source_workspace_is_given_while_visible_to_the_requester(self):
        self.assertIsNone(self.query_run(self.OWNER)["sourceWorkspace"])

        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(
            source_slug=self.WORKSPACE.slug
        )

        self.assertEqual(
            {"slug": self.WORKSPACE.slug},
            self.query_run(self.OWNER)["sourceWorkspace"],
        )

    def test_steps_follow_the_selected_resources_in_order(self):
        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(
            resources=["database", "files"],
            steps={"workspace": "SUCCESS", "files": "RUNNING"},
            status=WorkspaceCopyRunStatus.RUNNING,
        )

        self.assertEqual(
            [
                {"name": "WORKSPACE", "status": "SUCCESS"},
                {"name": "FILES", "status": "RUNNING"},
                {"name": "DATABASE", "status": "PENDING"},
            ],
            self.query_run(self.OWNER)["steps"],
        )

    def test_the_step_running_when_the_run_ended_is_the_one_that_failed(self):
        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(
            resources=["files"],
            steps={"workspace": "SUCCESS", "files": "RUNNING"},
            status=WorkspaceCopyRunStatus.FAILED,
            warnings=["1 file(s) could not be copied — see the logs for the list."],
        )

        run = self.query_run(self.OWNER)

        self.assertEqual({"name": "FILES", "status": "FAILED"}, run["steps"][1])
        self.assertEqual(
            ["1 file(s) could not be copied — see the logs for the list."],
            run["warnings"],
        )

    def test_the_workspace_is_null_until_created(self):
        WorkspaceCopyRun.objects.filter(id=self.RUN.id).update(result_workspace_slug="")

        self.assertIsNone(self.query_run(self.OWNER)["workspace"])
