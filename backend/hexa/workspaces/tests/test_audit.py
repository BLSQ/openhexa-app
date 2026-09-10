from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django_sql_dashboard.models import Dashboard

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import Dataset, DatasetLink
from hexa.user_management.models import Organization, User
from hexa.workspaces.authentication import WorkspaceToken
from hexa.workspaces.models import (
    TokenScopeVerdict,
    WorkspaceMembership,
    WorkspaceTokenUsage,
)
from hexa.workspaces.tests.testutils import create_workspace

WORKSPACE_QUERY = """
    query ($slug: String!) {
        workspace(slug: $slug) { slug }
    }
"""

DATASET_QUERY = """
    query ($id: ID!) {
        dataset(id: $id) { id }
    }
"""

DATASET_LINK_QUERY = """
    query ($workspaceSlug: String!, $datasetSlug: String!) {
        datasetLinkBySlug(workspaceSlug: $workspaceSlug, datasetSlug: $datasetSlug) {
            id
        }
    }
"""


class WorkspaceScopeAuditTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Audit Org")
        cls.USER = User.objects.create_user(
            "member@openhexa.org", "password", is_superuser=True
        )
        cls.SCOPE = create_workspace(
            cls.USER, name="Scoped Workspace", organization=cls.ORGANIZATION
        )
        cls.OTHER = create_workspace(
            cls.USER, name="Other Workspace", organization=cls.ORGANIZATION
        )
        cls.USER.is_superuser = False
        cls.USER.save()
        cls.MEMBERSHIP = WorkspaceMembership.objects.get(
            workspace=cls.SCOPE, user=cls.USER
        )

        cls.PRIVATE_DATASET = cls.create_dataset("Private", shared=False)
        cls.SHARED_DATASET = cls.create_dataset("Shared", shared=True)
        cls.LINKED_DATASET = cls.create_dataset("Linked", shared=False)
        DatasetLink.objects.create(dataset=cls.LINKED_DATASET, workspace=cls.SCOPE)

    @classmethod
    def create_dataset(cls, name: str, *, shared: bool) -> Dataset:
        """A dataset owned by the workspace the token is NOT scoped to."""
        dataset = Dataset.objects.create(
            name=name,
            slug=name.lower(),
            workspace=cls.OTHER,
            shared_with_organization=shared,
        )
        DatasetLink.objects.create(dataset=dataset, workspace=cls.OTHER)
        return dataset

    def query_with_token(self, query, variables):
        token = WorkspaceToken.issue(
            user=self.USER, workspace=self.SCOPE, membership=self.MEMBERSHIP
        )
        return self.run_query(
            query,
            variables,
            headers={"HTTP_AUTHORIZATION": f"Bearer {token.sign()}"},
        )

    def assertRecorded(self, verdict, foreign_workspaces=None):
        usage = WorkspaceTokenUsage.objects.get()
        self.assertEqual(usage.verdict, verdict)
        self.assertEqual(usage.workspace, self.SCOPE)
        self.assertEqual(usage.token_type, "membership")
        if foreign_workspaces is not None:
            self.assertEqual(usage.foreign_workspaces, foreign_workspaces)
        return usage

    def test_session_authenticated_requests_are_not_recorded(self):
        self.client.force_login(self.USER)
        self.run_query(WORKSPACE_QUERY, {"slug": self.OTHER.slug})
        self.assertFalse(WorkspaceTokenUsage.objects.exists())

    def test_request_within_the_token_workspace_is_in_scope(self):
        response = self.query_with_token(WORKSPACE_QUERY, {"slug": self.SCOPE.slug})
        self.assertEqual(response["data"]["workspace"]["slug"], self.SCOPE.slug)

        usage = self.assertRecorded(TokenScopeVerdict.IN_SCOPE, {})
        self.assertEqual(usage.root_fields, ["workspace"])

    def test_reaching_another_workspace_is_out_of_scope(self):
        response = self.query_with_token(WORKSPACE_QUERY, {"slug": self.OTHER.slug})
        self.assertEqual(response["data"]["workspace"]["slug"], self.OTHER.slug)

        self.assertRecorded(
            TokenScopeVerdict.OUT_OF_SCOPE, {str(self.OTHER.id): "none"}
        )

    def test_organization_shared_dataset_is_cross_reachable(self):
        self.query_with_token(DATASET_QUERY, {"id": str(self.SHARED_DATASET.id)})
        self.assertRecorded(
            TokenScopeVerdict.CROSS_REACHABLE, {str(self.OTHER.id): "org_shared"}
        )

    def test_linked_dataset_is_cross_reachable(self):
        self.query_with_token(DATASET_QUERY, {"id": str(self.LINKED_DATASET.id)})
        self.assertRecorded(
            TokenScopeVerdict.CROSS_REACHABLE, {str(self.OTHER.id): "linked"}
        )

    def test_dataset_of_another_workspace_is_out_of_scope(self):
        self.query_with_token(DATASET_QUERY, {"id": str(self.PRIVATE_DATASET.id)})
        self.assertRecorded(
            TokenScopeVerdict.OUT_OF_SCOPE, {str(self.OTHER.id): "none"}
        )

    def test_shared_dataset_read_from_its_source_workspace_is_cross_reachable(self):
        """The one documented cross-workspace SDK call: get_dataset(source_workspace_slug=...)."""
        self.query_with_token(
            DATASET_LINK_QUERY,
            {"workspaceSlug": self.OTHER.slug, "datasetSlug": "shared"},
        )
        self.assertRecorded(
            TokenScopeVerdict.CROSS_REACHABLE, {str(self.OTHER.id): "org_shared"}
        )

    def test_report_counts_tokens_that_would_break(self):
        self.query_with_token(WORKSPACE_QUERY, {"slug": self.SCOPE.slug})
        self.query_with_token(WORKSPACE_QUERY, {"slug": self.OTHER.slug})

        output = StringIO()
        call_command("workspace_token_report", stdout=output)
        report = output.getvalue()

        self.assertIn("active tokens              1", report)
        self.assertIn("would break if scoped      1 (100.0%)", report)
        self.assertIn("out-of-scope requests      1 (50.0%)", report)


class TokenScopeDashboardTest(TestCase):
    """The dashboard is seeded by migration, so its SQL is only checked at runtime."""

    def test_every_dashboard_query_runs_against_the_current_schema(self):
        dashboard = Dashboard.objects.get(slug="workspace-token-scope")
        self.assertEqual(dashboard.view_policy, "superuser")

        widgets = []
        with connection.cursor() as cursor:
            for query in dashboard.queries.all():
                cursor.execute(query.sql)
                widgets.append("-".join(sorted(c.name for c in cursor.description)))

        # django-sql-dashboard picks a widget template from the column names, so
        # a renamed column silently downgrades a chart to a plain table.
        self.assertEqual(
            widgets[:6],
            [
                "markdown",
                "big_number-label",
                "big_number-label",
                "completed_count-total_count",
                "bar_label-bar_quantity",
                "bar_label-bar_quantity",
            ],
        )
