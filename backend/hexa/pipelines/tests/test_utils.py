import uuid
from unittest.mock import MagicMock, PropertyMock, patch

from django.core import mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from hexa.core.test import TestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineNotificationLevel,
    PipelineRecipient,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
    PipelineVersion,
)
from hexa.pipelines.utils import (
    SkipReason,
    generate_pipeline_container_name,
    get_skip_reason,
    mail_skipped_run_recipients,
)
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace


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
        self.assertIn("my-works", container_name)  # truncated "my-workspace"
        self.assertIn("get-camp", container_name)  # truncated "get-campaigns"

        run.pipeline.workspace.slug = "MyWorkspace"
        run.pipeline.code = "GetCampaigns"
        container_name = generate_pipeline_container_name(run)

        self.assertEqual(
            container_name, container_name.lower(), "Name should be lowercase"
        )


class MailSkippedRunRecipientsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "skipped_mail@bluesquarehub.com", "pwd", is_superuser=True
        )
        cls.WORKSPACE = create_workspace(cls.USER, name="SkippedMailWS", description="")
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Skipped Mail Pipeline",
            code="skipped_mail_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.ZIPFILE,
        )
        PipelineRecipient.objects.create(
            pipeline=cls.PIPELINE,
            user=cls.USER,
            notification_level=PipelineNotificationLevel.ALL,
        )

    def test_mail_reports_a_run_already_in_progress(self):
        mail_skipped_run_recipients(
            self.PIPELINE, timezone.now(), SkipReason.run_already_in_progress()
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("already queued or running", mail.outbox[0].body)

    def test_mail_names_the_parameters_without_a_value(self):
        mail_skipped_run_recipients(
            self.PIPELINE,
            timezone.now(),
            SkipReason.missing_required_parameters(["country", "year"]),
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("country, year", mail.outbox[0].body)


class GetSkipReasonTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "skip_reason@bluesquarehub.com", "pwd", is_superuser=True
        )
        cls.WORKSPACE = create_workspace(cls.USER, name="SkipReasonWS", description="")
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Skip Reason Pipeline",
            code="skip_reason_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.ZIPFILE,
        )
        cls.VERSION = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            user=cls.USER,
            name="v1",
            parameters=[],
        )

    def _add_required_parameter(self, code: str):
        self.VERSION.parameters = self.VERSION.parameters + [
            {"code": code, "name": code, "type": "str", "required": True}
        ]
        self.VERSION.save()

    def test_no_reason_when_the_pipeline_can_run(self):
        self.assertIsNone(get_skip_reason(self.PIPELINE))

    def test_names_the_parameters_without_a_value(self):
        self._add_required_parameter("country")
        self._add_required_parameter("year")

        reason = get_skip_reason(self.PIPELINE)

        self.assertIn("country, year", str(reason.reason))

    def test_falls_back_to_a_generic_reason_when_the_cause_cannot_be_named(self):
        """An unschedulable pipeline with no missing parameter still has to skip the run.

        Guards against a future cause of unschedulability being reported as an empty list of
        missing parameters, or going unnoticed altogether.
        """
        with patch.object(
            Pipeline, "is_schedulable", new_callable=PropertyMock, return_value=False
        ):
            reason = get_skip_reason(self.PIPELINE)

        self.assertEqual(reason, SkipReason.not_schedulable())

    def test_reports_a_run_already_in_progress(self):
        PipelineRun.objects.create(
            user=None,
            pipeline=self.PIPELINE,
            pipeline_version=self.VERSION,
            run_id="in_progress",
            trigger_mode=PipelineRunTrigger.SCHEDULED,
            execution_date=timezone.now(),
            state=PipelineRunState.RUNNING,
        )

        reason = get_skip_reason(self.PIPELINE)

        self.assertEqual(reason, SkipReason.run_already_in_progress())
