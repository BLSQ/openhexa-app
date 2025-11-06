import os
from datetime import timedelta
from unittest.mock import MagicMock, Mock, patch

from django.test import TestCase, override_settings
from django.utils import timezone
from kubernetes.client import ApiException

from hexa.pipelines.management.commands.pipelines_runner import (
    attach_to_pod_kube,
    create_pod_kube,
    monitor_pod_kube,
    process_zombie_runs,
    run_pipeline,
)
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunLogLevel,
    PipelineRunState,
    PipelineType,
    PipelineVersion,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


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
            "HEXA_PIPELINE_CODE": "pipeline_code",
            "HEXA_LOG_LEVEL": str(PipelineRunLogLevel.DEBUG),
            "HEXA_NOTEBOOK_PATH": "/path/to/notebook",
        }
        mock_run_pipeline_docker.assert_called_once_with(
            mock_run, "docker_image", expected_env_vars
        )


class TestKubernetesPipelineIntegration(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.workspace = Workspace.objects.create(
            slug="test-workspace",
            name="Test Workspace",
        )
        self.pipeline = Pipeline.objects.create(
            workspace=self.workspace,
            code="test_pipeline",
            name="Test Pipeline",
            type=PipelineType.ZIPFILE,
            cpu_limit="1000m",
            memory_limit="1Gi",
            cpu_request="100m",
            memory_request="256Mi",
        )
        self.version = PipelineVersion.objects.create(
            pipeline=self.pipeline,
            name="v1",
            timeout=300,
        )
        self.run = PipelineRun.objects.create(
            pipeline=self.pipeline,
            pipeline_version=self.version,
            state=PipelineRunState.QUEUED,
            config={"test": "config"},
            send_mail_notifications=False,
            timeout=300,
            execution_date=timezone.now(),
        )

    def _create_mock_pod(self, phase="Succeeded", reason=None):
        """Helper to create a mock pod object"""
        mock_pod = Mock()
        mock_pod.metadata.name = f"pipeline-{self.run.id}"
        mock_pod.metadata.namespace = "default"
        mock_pod.status.phase = phase
        mock_pod.status.reason = reason
        return mock_pod

    def _create_mock_kubernetes_api(self, pod_phase="Succeeded", pod_reason=None):
        """Helper to create mock K8s API with realistic behavior"""
        mock_api = Mock()
        mock_pod = self._create_mock_pod(phase=pod_phase, reason=pod_reason)

        mock_api.create_namespaced_pod.return_value = mock_pod
        mock_api.read_namespaced_pod.return_value = mock_pod
        mock_api.read_namespaced_pod_log.return_value = "Pipeline execution logs"
        mock_api.delete_namespaced_pod.return_value = None

        return mock_api

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_create_pod_with_correct_configuration(
        self, mock_k8s_client, mock_config, mock_sleep
    ):
        mock_api = self._create_mock_kubernetes_api()
        mock_k8s_client.return_value = mock_api

        env_vars = {
            "HEXA_WORKSPACE": "test-workspace",
            "HEXA_RUN_ID": str(self.run.id),
        }

        create_pod_kube(self.run, "test-image:latest", env_vars)

        mock_api.create_namespaced_pod.assert_called_once()
        call_args = mock_api.create_namespaced_pod.call_args

        self.assertEqual(call_args[1]["namespace"], "default")

        pod_spec = call_args[1]["body"]
        self.assertEqual(pod_spec.metadata.labels["hexa-run-id"], str(self.run.id))
        self.assertEqual(pod_spec.spec.active_deadline_seconds, 300)

        container = pod_spec.spec.containers[0]
        self.assertEqual(container.image, "test-image:latest")
        self.assertEqual(container.resources["limits"]["cpu"], "1000m")
        self.assertEqual(container.resources["limits"]["memory"], "1Gi")

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_successful_pipeline_execution_end_to_end(
        self, mock_k8s_client, mock_config, mock_sleep
    ):
        mock_api = self._create_mock_kubernetes_api("Succeeded")
        mock_k8s_client.return_value = mock_api

        env_vars = {
            "HEXA_WORKSPACE": "test-workspace",
            "HEXA_RUN_ID": str(self.run.id),
        }

        pod = create_pod_kube(self.run, "test-image:latest", env_vars)
        success, logs = monitor_pod_kube(self.run, pod)

        self.run.refresh_from_db()
        self.assertTrue(success)
        self.assertIn("Pipeline execution logs", logs)

        mock_api.create_namespaced_pod.assert_called_once()
        mock_api.read_namespaced_pod_log.assert_called_once()
        mock_api.delete_namespaced_pod.assert_called_once()

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_failed_pipeline_execution(self, mock_k8s_client, mock_config, mock_sleep):
        mock_api = self._create_mock_kubernetes_api("Failed")
        mock_k8s_client.return_value = mock_api

        env_vars = {
            "HEXA_WORKSPACE": "test-workspace",
            "HEXA_RUN_ID": str(self.run.id),
        }

        pod = create_pod_kube(self.run, "test-image:latest", env_vars)
        success, logs = monitor_pod_kube(self.run, pod)

        self.assertFalse(success)
        self.assertIn("Pipeline execution logs", logs)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_pipeline_timeout_handling(self, mock_k8s_client, mock_config, mock_sleep):
        mock_api = self._create_mock_kubernetes_api("Failed", "DeadlineExceeded")
        mock_k8s_client.return_value = mock_api

        env_vars = {
            "HEXA_WORKSPACE": "test-workspace",
            "HEXA_RUN_ID": str(self.run.id),
        }

        pod = create_pod_kube(self.run, "test-image:latest", env_vars)
        success, logs = monitor_pod_kube(self.run, pod)

        self.assertFalse(success)
        self.assertIn(f"Timeout killed run {self.run.pipeline.name}", logs)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_monitor_updates_heartbeat(self, mock_k8s_client, mock_config, mock_sleep):
        call_count = [0]

        def pod_progression(*args, **kwargs):
            call_count[0] += 1
            phase = "Succeeded" if call_count[0] >= 2 else "Running"
            return self._create_mock_pod(phase)

        mock_api = Mock()
        mock_api.read_namespaced_pod.side_effect = pod_progression
        mock_api.read_namespaced_pod_log.return_value = "logs"
        mock_api.delete_namespaced_pod.return_value = None
        mock_k8s_client.return_value = mock_api

        initial_heartbeat = self.run.last_heartbeat
        pod = self._create_mock_pod("Running")

        monitor_pod_kube(self.run, pod)

        self.run.refresh_from_db()
        self.assertIsNotNone(self.run.last_heartbeat)
        self.assertGreater(self.run.last_heartbeat, initial_heartbeat)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_attach_to_existing_pod(self, mock_k8s_client, mock_config, mock_sleep):
        mock_api = self._create_mock_kubernetes_api()
        mock_k8s_client.return_value = mock_api

        self.run.state = PipelineRunState.RUNNING
        self.run.save()

        pod = attach_to_pod_kube(self.run)

        mock_api.read_namespaced_pod.assert_called_once()
        mock_api.create_namespaced_pod.assert_not_called()
        self.assertIsNotNone(pod)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_pod_logs_retrieval_failure_handled(
        self, mock_k8s_client, mock_config, mock_sleep
    ):
        mock_api = self._create_mock_kubernetes_api("Succeeded")
        mock_api.read_namespaced_pod_log.side_effect = Exception("Logs unavailable")
        mock_k8s_client.return_value = mock_api

        env_vars = {
            "HEXA_WORKSPACE": "test-workspace",
            "HEXA_RUN_ID": str(self.run.id),
        }

        pod = create_pod_kube(self.run, "test-image:latest", env_vars)
        success, logs = monitor_pod_kube(self.run, pod)

        self.assertTrue(success)
        self.assertEqual(logs, "")

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("hexa.pipelines.management.commands.pipelines_runner.sleep")
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_pod_deletion_404_ignored(self, mock_k8s_client, mock_config, mock_sleep):
        mock_api = self._create_mock_kubernetes_api("Succeeded")

        api_exception = ApiException(status=404)
        mock_api.delete_namespaced_pod.side_effect = api_exception
        mock_k8s_client.return_value = mock_api

        env_vars = {
            "HEXA_WORKSPACE": "test-workspace",
            "HEXA_RUN_ID": str(self.run.id),
        }

        pod = create_pod_kube(self.run, "test-image:latest", env_vars)
        success, logs = monitor_pod_kube(self.run, pod)

        self.assertTrue(success)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_zombie_run_without_pod_marked_failed(self, mock_k8s_client, mock_config):
        old_time = timezone.now() - timedelta(minutes=20)
        self.run.state = PipelineRunState.RUNNING
        self.run.last_heartbeat = old_time
        self.run.save()

        mock_api = mock_k8s_client.return_value
        mock_api.list_namespaced_pod.return_value.items = []

        process_zombie_runs()

        self.run.refresh_from_db()
        self.assertEqual(self.run.state, PipelineRunState.FAILED)
        self.assertIn("Killed due to heartbeat timeout", self.run.run_logs)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_zombie_run_with_completed_pod_gets_final_state(
        self, mock_k8s_client, mock_config
    ):
        old_time = timezone.now() - timedelta(minutes=20)
        self.run.state = PipelineRunState.RUNNING
        self.run.last_heartbeat = old_time
        self.run.save()

        mock_api = mock_k8s_client.return_value
        mock_pod = self._create_mock_pod("Succeeded")
        mock_pod.spec.containers = [Mock(name="test-container")]
        mock_api.list_namespaced_pod.return_value.items = [mock_pod]
        mock_api.read_namespaced_pod_log.return_value = "Final pod logs"

        process_zombie_runs()

        self.run.refresh_from_db()
        self.assertEqual(self.run.state, PipelineRunState.SUCCESS)
        self.assertEqual(self.run.run_logs, "Final pod logs")

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="kubernetes")
    @patch.dict(os.environ, {"IS_LOCAL_DEV": "False"}, clear=False)
    @patch("kubernetes.config.load_incluster_config")
    @patch("kubernetes.client.CoreV1Api")
    def test_zombie_run_with_running_pod_still_marked_failed(
        self, mock_k8s_client, mock_config
    ):
        old_time = timezone.now() - timedelta(minutes=20)
        self.run.state = PipelineRunState.RUNNING
        self.run.last_heartbeat = old_time
        self.run.run_logs = "Old logs"
        self.run.save()

        mock_api = mock_k8s_client.return_value
        mock_pod = self._create_mock_pod("Running")
        mock_pod.spec.containers = [Mock(name="test-container")]
        mock_api.list_namespaced_pod.return_value.items = [mock_pod]
        mock_api.read_namespaced_pod_log.return_value = "Current pod logs"

        process_zombie_runs()

        self.run.refresh_from_db()
        self.assertEqual(self.run.state, PipelineRunState.FAILED)
        self.assertIn("Killed due to heartbeat timeout", self.run.run_logs)

    @override_settings(PIPELINE_SCHEDULER_SPAWNER="docker")
    def test_zombie_runs_for_docker_spawner(self):
        old_time = timezone.now() - timedelta(minutes=20)
        self.run.state = PipelineRunState.RUNNING
        self.run.last_heartbeat = old_time
        self.run.save()

        process_zombie_runs()

        self.run.refresh_from_db()
        self.assertEqual(self.run.state, PipelineRunState.FAILED)
        self.assertIn("Killed due to heartbeat timeout", self.run.run_logs)
