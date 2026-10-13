from django.contrib.auth.models import AnonymousUser

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVisibility,
)
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

PUBLIC_PIPELINE_QUERY = """
    query ($id: UUID!) {
        publicPipeline(id: $id) {
            id name description visibility runnable organizationName
            parameters { code type default required }
        }
    }
"""

PUBLIC_RUN_QUERY = """
    query ($id: UUID!) {
        publicPipelineRun(id: $id) {
            id status progress config
            messages { message priority }
            pipeline { id name }
        }
    }
"""

RUN_PUBLIC_MUTATION = """
    mutation ($input: RunPublicPipelineInput!) {
        runPublicPipeline(input: $input) {
            success errors run { id status pipeline { id } }
        }
    }
"""

UPDATE_MUTATION = """
    mutation ($input: UpdatePipelineInput!) {
        updatePipeline(input: $input) {
            success errors details pipeline { visibility permissions { publish } }
        }
    }
"""


class PublicPipelinesSchemaTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Public Org")
        cls.USER_OWNER = User.objects.create_user("owner@bluesquarehub.com", "pw")
        cls.USER_EDITOR = User.objects.create_user("editor@bluesquarehub.com", "pw")
        cls.USER_OUTSIDER = User.objects.create_user("out@bluesquarehub.com", "pw")
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_OWNER,
            role=OrganizationMembershipRole.OWNER,
        )
        cls.WORKSPACE = create_workspace(
            cls.USER_OWNER, name="WS", organization=cls.ORGANIZATION
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE, name="Public P", code="public-p", description="d"
        )
        cls.PIPELINE.upload_new_version(
            cls.USER_OWNER,
            zipfile=b"",
            name="v1",
            parameters=[
                {"code": "count", "name": "Count", "type": "int", "required": True},
                {"code": "token", "name": "Token", "type": "secret"},
                {
                    "code": "dhis",
                    "name": "DHIS2",
                    "type": "dhis2",
                    "required": True,
                    "default": "dhis2-play",
                },
            ],
        )
        cls.PRIVATE = Pipeline.objects.create(
            workspace=cls.WORKSPACE, name="Private P", code="private-p"
        )
        cls.PRIVATE.upload_new_version(
            cls.USER_OWNER, zipfile=b"", name="v1", parameters=[]
        )

    def setUp(self):
        super().setUp()
        self.PIPELINE.visibility = PipelineVisibility.PUBLIC
        self.PIPELINE.save()

    # --- reading ---

    def test_anonymous_visitor_reads_a_public_pipeline(self):
        r = self.run_query(PUBLIC_PIPELINE_QUERY, {"id": str(self.PIPELINE.id)})
        pipeline = r["data"]["publicPipeline"]
        self.assertEqual(pipeline["name"], "Public P")
        self.assertEqual(pipeline["visibility"], "PUBLIC")
        self.assertTrue(pipeline["runnable"])
        self.assertEqual(pipeline["organizationName"], "Public Org")
        self.assertEqual(
            [p["code"] for p in pipeline["parameters"]], ["count", "token"]
        )

    def test_a_pipeline_that_is_not_public_is_null_for_everyone(self):
        for user in (None, self.USER_EDITOR):
            if user:
                self.client.force_login(user)
            r = self.run_query(PUBLIC_PIPELINE_QUERY, {"id": str(self.PRIVATE.id)})
            self.assertIsNone(r["data"]["publicPipeline"])

    def test_member_only_queries_stay_closed_to_visitors(self):
        r = self.run_query(
            "query ($id: UUID!) { pipeline(id: $id) { id } }",
            {"id": str(self.PIPELINE.id)},
        )
        self.assertIsNone(r["data"]["pipeline"])
        self.assertEqual(r["errors"][0]["extensions"]["code"], "UNAUTHENTICATED")

    def test_outsider_cannot_reach_the_full_pipeline(self):
        self.client.force_login(self.USER_OUTSIDER)
        r = self.run_query(
            "query ($id: UUID!) { pipeline(id: $id) { id } }",
            {"id": str(self.PIPELINE.id)},
        )
        self.assertIsNone(r["data"]["pipeline"])

    def test_pipeline_runs_listing_is_untouched(self):
        self.client.force_login(self.USER_OUTSIDER)
        r = self.run_query("{ pipelines { items { id } } }")
        self.assertEqual(r["data"]["pipelines"]["items"], [])

    # --- running ---

    def test_anonymous_visitor_runs_a_public_pipeline(self):
        r = self.run_query(
            RUN_PUBLIC_MUTATION,
            {"input": {"id": str(self.PIPELINE.id), "config": {"count": 2}}},
        )
        result = r["data"]["runPublicPipeline"]
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["success"])
        self.assertEqual(result["run"]["status"], "queued")
        run = PipelineRun.objects.get(id=result["run"]["id"])
        self.assertIsNone(run.user)
        self.assertEqual(run.trigger_mode, PipelineRunTrigger.PUBLIC)

    def test_run_errors(self):
        r = self.run_query(
            RUN_PUBLIC_MUTATION,
            {"input": {"id": str(self.PRIVATE.id), "config": {}}},
        )
        self.assertEqual(
            r["data"]["runPublicPipeline"]["errors"], ["PIPELINE_NOT_FOUND"]
        )

        r = self.run_query(
            RUN_PUBLIC_MUTATION,
            {"input": {"id": str(self.PIPELINE.id), "config": {"count": "two"}}},
        )
        self.assertEqual(r["data"]["runPublicPipeline"]["errors"], ["INVALID_CONFIG"])

        self.run_query(
            RUN_PUBLIC_MUTATION,
            {"input": {"id": str(self.PIPELINE.id), "config": {"count": 1}}},
        )
        r = self.run_query(
            RUN_PUBLIC_MUTATION,
            {"input": {"id": str(self.PIPELINE.id), "config": {"count": 1}}},
        )
        self.assertEqual(
            r["data"]["runPublicPipeline"]["errors"], ["PUBLIC_RUN_IN_PROGRESS"]
        )

    def test_run_not_runnable(self):
        self.PIPELINE.upload_new_version(
            self.USER_OWNER,
            zipfile=b"",
            name="v2",
            parameters=[
                {"code": "ds", "name": "Dataset", "type": "dataset", "required": True}
            ],
        )
        r = self.run_query(PUBLIC_PIPELINE_QUERY, {"id": str(self.PIPELINE.id)})
        self.assertFalse(r["data"]["publicPipeline"]["runnable"])
        r = self.run_query(
            RUN_PUBLIC_MUTATION,
            {"input": {"id": str(self.PIPELINE.id), "config": {}}},
        )
        self.assertEqual(
            r["data"]["runPublicPipeline"]["errors"], ["PIPELINE_NOT_RUNNABLE"]
        )

    # --- following a run ---

    def test_visitor_follows_their_run_by_id(self):
        run = self.PIPELINE.run_public(AnonymousUser(), {"count": 1, "token": "s3cret"})
        run.log_message("INFO", "hello")
        r = self.run_query(PUBLIC_RUN_QUERY, {"id": str(run.id)})
        data = r["data"]["publicPipelineRun"]
        self.assertEqual(data["status"], "queued")
        self.assertEqual(data["messages"], [{"message": "hello", "priority": "INFO"}])
        self.assertEqual(data["pipeline"]["name"], "Public P")
        # The visitor's own values, without the secret or the connection fallback.
        self.assertEqual(data["config"], {"count": 1})

    def test_a_members_run_is_not_a_public_run(self):
        run = self.PIPELINE.run(
            user=self.USER_EDITOR,
            pipeline_version=self.PIPELINE.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={"count": 1},
        )
        r = self.run_query(PUBLIC_RUN_QUERY, {"id": str(run.id)})
        self.assertIsNone(r["data"]["publicPipelineRun"])

    def test_unpublishing_closes_the_run_pages(self):
        run = self.PIPELINE.run_public(AnonymousUser(), {"count": 1})
        run.state = PipelineRunState.SUCCESS
        run.save()
        self.PIPELINE.visibility = PipelineVisibility.WORKSPACE
        self.PIPELINE.save()
        r = self.run_query(PUBLIC_RUN_QUERY, {"id": str(run.id)})
        self.assertIsNone(r["data"]["publicPipelineRun"])

    # --- publishing ---

    def test_publish_permission(self):
        query = """
            query ($id: UUID!) { pipeline(id: $id) { permissions { publish update } } }
        """
        self.client.force_login(self.USER_OWNER)
        r = self.run_query(query, {"id": str(self.PRIVATE.id)})
        self.assertEqual(
            r["data"]["pipeline"]["permissions"], {"publish": True, "update": True}
        )
        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(query, {"id": str(self.PRIVATE.id)})
        self.assertEqual(
            r["data"]["pipeline"]["permissions"], {"publish": False, "update": True}
        )

    def test_update_visibility(self):
        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            UPDATE_MUTATION,
            {"input": {"id": str(self.PRIVATE.id), "visibility": "PUBLIC"}},
        )
        self.assertEqual(r["data"]["updatePipeline"]["errors"], ["PERMISSION_DENIED"])

        self.client.force_login(self.USER_OWNER)
        r = self.run_query(
            UPDATE_MUTATION,
            {"input": {"id": str(self.PRIVATE.id), "visibility": "PUBLIC"}},
        )
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])
        self.assertEqual(
            r["data"]["updatePipeline"]["pipeline"]["visibility"], "PUBLIC"
        )

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            UPDATE_MUTATION,
            {"input": {"id": str(self.PRIVATE.id), "visibility": "WORKSPACE"}},
        )
        self.assertEqual(r["data"]["updatePipeline"]["errors"], [])
        self.assertEqual(
            r["data"]["updatePipeline"]["pipeline"]["visibility"], "WORKSPACE"
        )

    def test_update_visibility_names_the_missing_defaults(self):
        self.PRIVATE.upload_new_version(
            self.USER_OWNER,
            zipfile=b"",
            name="v2",
            parameters=[
                {"code": "ds", "name": "Dataset", "type": "dataset", "required": True}
            ],
        )
        self.client.force_login(self.USER_OWNER)
        r = self.run_query(
            UPDATE_MUTATION,
            {"input": {"id": str(self.PRIVATE.id), "visibility": "PUBLIC"}},
        )
        self.assertEqual(
            r["data"]["updatePipeline"]["errors"], ["MISSING_VERSION_CONFIG"]
        )
        self.assertEqual(r["data"]["updatePipeline"]["details"], "ds")
