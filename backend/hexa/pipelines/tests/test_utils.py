import uuid
from unittest.mock import MagicMock

from django.utils.crypto import get_random_string

from hexa.core.test import TestCase
from hexa.pipelines.utils import generate_pipeline_container_name


class PipelineUtilsTest(TestCase):
    def test_generate_pipeline_container_name_length(self):
        """Test that generated names are within Kubernetes 63-character limit."""
        run = MagicMock()
        run.id = uuid.uuid4()
        run.pipeline.workspace.slug = get_random_string(50)
        run.pipeline.code = get_random_string(50)

        container_name = generate_pipeline_container_name(run)
        self.assertTrue(len(container_name) <= 63)

        run.pipeline.workspace.slug = get_random_string(100)
        run.pipeline.code = get_random_string(100)

        container_name = generate_pipeline_container_name(run)
        self.assertTrue(len(container_name) <= 63)

    def test_generate_pipeline_container_name_determinism(self):
        """Test that the same run generates the same container name (deterministic)."""
        run = MagicMock()
        run_id = uuid.uuid4()
        run.id = run_id
        run.pipeline.workspace.slug = "my-workspace"
        run.pipeline.code = "my-pipeline"

        container_name_1 = generate_pipeline_container_name(run)
        container_name_2 = generate_pipeline_container_name(run)

        self.assertEqual(
            container_name_1,
            container_name_2,
            "Container name should be deterministic for the same run",
        )

        self.assertTrue(container_name_1.startswith("pipeline-"))
        self.assertIn(str(run_id), container_name_1)
        self.assertIn("my-work", container_name_1)
        self.assertIn("my-pipe", container_name_1)

    def test_generate_pipeline_container_name_uniqueness(self):
        """Test that different runs generate different container names."""
        run1 = MagicMock()
        run1.id = uuid.uuid4()
        run1.pipeline.workspace.slug = "workspace"
        run1.pipeline.code = "pipeline"

        run2 = MagicMock()
        run2.id = uuid.uuid4()
        run2.pipeline.workspace.slug = "workspace"
        run2.pipeline.code = "pipeline"

        container_name_1 = generate_pipeline_container_name(run1)
        container_name_2 = generate_pipeline_container_name(run2)

        self.assertNotEqual(
            container_name_1,
            container_name_2,
            "Container names should be unique for different runs",
        )

    def test_generate_pipeline_container_name_rfc1123_compliance(self):
        """Test that generated names comply with RFC 1123 (lowercase alphanumeric + hyphens)."""
        run = MagicMock()
        run.id = uuid.uuid4()

        run.pipeline.workspace.slug = "my_workspace"
        run.pipeline.code = "get_campaigns"
        container_name = generate_pipeline_container_name(run)

        self.assertNotIn(
            "_", container_name, "Underscores should be replaced with hyphens"
        )
        self.assertIn("my-workspace", container_name)
        self.assertIn("get-campaigns", container_name)

        run.pipeline.workspace.slug = "MyWorkspace"
        run.pipeline.code = "GetCampaigns"
        container_name = generate_pipeline_container_name(run)

        self.assertEqual(
            container_name, container_name.lower(), "Name should be lowercase"
        )
