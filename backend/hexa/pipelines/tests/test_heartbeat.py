from unittest.mock import patch

from django.core.signing import Signer

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class UpdatePipelineHeartbeatTest(GraphQLTestCase):
    """Test suite for the updatePipelineHeartbeat GraphQL mutation."""

    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WS1 = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS1",
                description="Workspace 1",
            )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WS1,
            name="Test Pipeline",
            code="test_pipeline",
            type=PipelineType.ZIPFILE,
        )

    def _create_pipeline_run(self, state=PipelineRunState.RUNNING):
        """Helper method to create a pipeline run with the given state."""
        run = self.PIPELINE.run(
            user=self.USER_ROOT,
            pipeline_version=None,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )
        run.state = state
        run.save()
        return run

    def test_update_heartbeat_success(self):
        """Test that a running pipeline can successfully update its heartbeat."""
        run = self._create_pipeline_run(PipelineRunState.RUNNING)
        initial_heartbeat = run.last_heartbeat
        signed_token = Signer().sign_object(run.access_token)

        r = self.run_query(
            """
            mutation {
                updatePipelineHeartbeat {
                    success
                    errors
                }
            }
            """,
            headers={"HTTP_AUTHORIZATION": f"Bearer {signed_token}"},
        )

        self.assertEqual(True, r["data"]["updatePipelineHeartbeat"]["success"])
        self.assertEqual([], r["data"]["updatePipelineHeartbeat"]["errors"])

        run.refresh_from_db()
        self.assertGreater(run.last_heartbeat, initial_heartbeat)

    def test_update_heartbeat_not_authenticated(self):
        """Test that unauthenticated requests are rejected."""
        self._create_pipeline_run(PipelineRunState.RUNNING)
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation {
                updatePipelineHeartbeat {
                    success
                    errors
                }
            }
            """,
        )

        self.assertEqual(False, r["data"]["updatePipelineHeartbeat"]["success"])
        self.assertEqual(
            ["PIPELINE_NOT_FOUND"], r["data"]["updatePipelineHeartbeat"]["errors"]
        )

    def test_update_heartbeat_pipeline_already_completed_success(self):
        """Test that completed (SUCCESS) pipelines cannot authenticate."""
        run = self._create_pipeline_run(PipelineRunState.SUCCESS)
        initial_heartbeat = run.last_heartbeat
        signed_token = Signer().sign_object(run.access_token)

        r = self.run_query(
            """
            mutation {
                updatePipelineHeartbeat {
                    success
                    errors
                }
            }
            """,
            headers={"HTTP_AUTHORIZATION": f"Bearer {signed_token}"},
        )

        self.assertEqual(False, r["data"]["updatePipelineHeartbeat"]["success"])
        self.assertEqual(
            ["PIPELINE_NOT_FOUND"],
            r["data"]["updatePipelineHeartbeat"]["errors"],
        )
        run.refresh_from_db()
        self.assertEqual(run.last_heartbeat, initial_heartbeat)
