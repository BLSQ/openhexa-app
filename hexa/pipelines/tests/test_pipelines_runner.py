from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from hexa.pipelines.management.commands.pipelines_runner import run_pipeline
from hexa.pipelines.models import PipelineRun, PipelineRunLogLevel, PipelineType


class TestRunPipeline(TestCase):
    @override_settings(
        INTERNAL_BASE_URL="http://testserver",
        DEFAULT_WORKSPACE_IMAGE="default_workspace_image",
        PIPELINE_SCHEDULER_SPAWNER="docker",
    )
    @patch("hexa.pipelines.management.commands.pipelines_runner.run_pipeline_docker")
    @patch("os.fork", return_value=0)
    def test_env_vars(self, _, mock_run_pipeline_docker):
        mock_run = MagicMock(spec=PipelineRun)
        mock_run.id = 123
        mock_run.access_token = "someAccessToken"
        mock_run.log_level = PipelineRunLogLevel.DEBUG
        mock_run.pipeline.workspace.slug = "test_workspace"
        mock_run.pipeline.workspace.docker_image = "docker_image"
        mock_run.pipeline.name = "test_pipeline"
        mock_run.pipeline.type = PipelineType.NOTEBOOK
        mock_run.pipeline.notebook_path = "/path/to/notebook"
        mock_run.pipeline.code = "pipeline_code"
        mock_run.send_mail_notifications = False

        mock_run_pipeline_docker.return_value = (True, "SomeLogs")

        with self.assertRaises(SystemExit):
            run_pipeline(mock_run)

        expected_env_vars = {
            "HEXA_SERVER_URL": "http://testserver",
            "HEXA_TOKEN": "InNvbWVBY2Nlc3NUb2tlbiI:6jqo7CX79O6IOh7lgqpwOXBBYSxzNOBtXeSNb4ry9EM",
            "HEXA_WORKSPACE": "test_workspace",
            "HEXA_RUN_ID": "123",
            "HEXA_PIPELINE_NAME": "test_pipeline",
            "HEXA_PIPELINE_TYPE": PipelineType.NOTEBOOK,
            "HEXA_LOG_LEVEL": str(PipelineRunLogLevel.DEBUG),
            "HEXA_NOTEBOOK_PATH": "/path/to/notebook",
        }
        mock_run_pipeline_docker.assert_called_once_with(
            mock_run, "docker_image", expected_env_vars
        )
