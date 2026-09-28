from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.user_management.models import Organization, User
from hexa.workspaces.audit import WorkspaceScopeAudit, audit_extensions
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

DATASET_VERSION_FILE_QUERY = """
    query ($id: ID!) {
        datasetVersionFile(id: $id) { id }
    }
"""

DATASET_LINK_QUERY = """
    query ($workspaceSlug: String!, $datasetSlug: String!) {
        datasetLinkBySlug(workspaceSlug: $workspaceSlug, datasetSlug: $datasetSlug) {
            id
        }
    }
"""


WORKSPACE_DATASETS_QUERY = """
    query ($slug: String!) {
        workspace(slug: $slug) {
            slug
            datasets { items { dataset { slug } } }
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

    def test_the_extension_is_only_installed_for_token_requests(self):
        """It is GraphQL middleware, so it must not be attached to untokened traffic."""
        request = RequestFactory().post("/graphql/")
        self.assertEqual([], audit_extensions(request, None))

        request.workspace_token = WorkspaceToken.issue(
            user=self.USER, workspace=self.SCOPE, membership=self.MEMBERSHIP
        )
        self.assertEqual([WorkspaceScopeAudit], audit_extensions(request, None))

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

    def test_every_object_of_a_multi_object_response_is_attributed(self):
        """The per-object short-circuit must not skip objects, only repeated fields."""
        response = self.query_with_token(
            WORKSPACE_DATASETS_QUERY, {"slug": self.OTHER.slug}
        )
        items = response["data"]["workspace"]["datasets"]["items"]
        self.assertEqual(
            {"linked", "private", "shared"}, {item["dataset"]["slug"] for item in items}
        )
        self.assertRecorded(
            TokenScopeVerdict.CROSS_REACHABLE, {str(self.OTHER.id): "linked"}
        )

    def test_resolve_observes_every_distinct_object(self):
        """Repeated fields of one object are skipped; a different object never is."""
        audit = WorkspaceScopeAudit()
        info = SimpleNamespace(path=SimpleNamespace(prev=None), field_name="dataset")
        for dataset in (
            self.PRIVATE_DATASET,
            self.PRIVATE_DATASET,
            self.SHARED_DATASET,
            self.SHARED_DATASET,
            self.LINKED_DATASET,
        ):
            audit.resolve(lambda obj, info, **kwargs: None, dataset, info)

        self.assertEqual({self.OTHER.id: {"Dataset"}}, audit.models_by_workspace)
        self.assertEqual(
            {
                self.PRIVATE_DATASET.id,
                self.SHARED_DATASET.id,
                self.LINKED_DATASET.id,
            },
            audit.dataset_ids,
        )

    def test_dataset_version_file_is_attributed_to_the_dataset_workspace(self):
        """A file carries no workspace of its own, so it is resolved through its version."""
        version = DatasetVersion.objects.create(
            dataset=self.PRIVATE_DATASET, name="v1", created_by=self.USER
        )
        file = DatasetVersionFile.objects.create(
            dataset_version=version, uri="s3://private/v1/data.csv", content_type="csv"
        )

        self.query_with_token(DATASET_VERSION_FILE_QUERY, {"id": str(file.id)})

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


class TokenScopeSummaryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ALICE = User.objects.create_user(
            "alice@openhexa.org", "password", is_superuser=True, is_staff=True
        )
        cls.BOB = User.objects.create_user("bob@openhexa.org", "password")
        cls.WORKSPACE = create_workspace(cls.ALICE, name="Audited Workspace")

        # Two identity sessions of Alice's count as one token, Bob's cross-workspace
        # but legal token as another, and his in-scope membership token as a third.
        cls.record(cls.ALICE, "identity", TokenScopeVerdict.OUT_OF_SCOPE, "session-1")
        cls.record(cls.ALICE, "identity", TokenScopeVerdict.OUT_OF_SCOPE, "session-2")
        cls.record(cls.ALICE, "identity", TokenScopeVerdict.IN_SCOPE, "session-2")
        cls.record(cls.BOB, "identity", TokenScopeVerdict.CROSS_REACHABLE, "session-3")
        cls.record(cls.BOB, "membership", TokenScopeVerdict.IN_SCOPE, "membership")

    @classmethod
    def record(cls, user, token_type, verdict, fingerprint):
        WorkspaceTokenUsage.objects.create(
            token_fingerprint=fingerprint,
            token_type=token_type,
            user=user,
            workspace=cls.WORKSPACE,
            verdict=verdict,
        )

    def test_scope_summary_counts_tokens_by_what_they_were_issued_for(self):
        summary = WorkspaceTokenUsage.objects.scope_summary()

        self.assertEqual(
            {
                "tokens": 3,
                "breaking": 1,
                "reaching": 1,
                "requests": 5,
                "out_of_scope_requests": 2,
            },
            {key: value for key, value in summary.items() if key != "top_breaking"},
        )
        [top] = summary["top_breaking"]
        self.assertEqual(top["user__email"], self.ALICE.email)
        self.assertEqual(top["requests"], 2)

    def test_scope_summary_of_no_requests(self):
        summary = WorkspaceTokenUsage.objects.none().scope_summary()
        self.assertEqual(summary["tokens"], 0)
        self.assertEqual(summary["requests"], 0)

    def test_admin_summarises_the_filtered_requests(self):
        self.client.force_login(self.ALICE)
        response = self.client.get(
            "/admin/workspaces/workspacetokenusage/",
            # The same filters the top breaking tokens link to.
            {"user": self.BOB.id, "token_type__exact": "membership"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["tokens"], 1)
        self.assertContains(response, "Would break if scoped")
