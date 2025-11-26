from unittest.mock import patch

from django.utils import timezone

from hexa.core.test import TestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
    PipelineVersion,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class PipelineSchedulerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com",
            "admin",
            is_superuser=True,
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Sandbox",
            description="Test workspace",
            countries=[{"code": "AL"}],
        )
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Pipeline",
            code="test_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.NOTEBOOK,
        )
        cls.VERSION = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            name="v1",
            parameters=[],
        )

    def test_scheduled_run_skipped_when_queued_run_exists(self):
        PipelineRun.objects.create(
            pipeline=self.PIPELINE,
            pipeline_version=self.VERSION,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.QUEUED,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(
                pipeline=self.PIPELINE
            ).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertTrue(should_skip)

            final_run_count = PipelineRun.objects.filter(pipeline=self.PIPELINE).count()
            self.assertEqual(
                final_run_count,
                initial_run_count,
            )

    def test_scheduled_run_skipped_when_running_run_exists(self):
        PipelineRun.objects.create(
            pipeline=self.PIPELINE,
            pipeline_version=self.VERSION,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.RUNNING,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(
                pipeline=self.PIPELINE
            ).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertTrue(should_skip)

            final_run_count = PipelineRun.objects.filter(pipeline=self.PIPELINE).count()
            self.assertEqual(
                final_run_count,
                initial_run_count,
            )

    def test_scheduled_run_allowed_when_previous_run_completed(self):
        PipelineRun.objects.create(
            pipeline=self.PIPELINE,
            pipeline_version=self.VERSION,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.SUCCESS,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(
                pipeline=self.PIPELINE
            ).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertFalse(should_skip)

            self.PIPELINE.run(
                user=None,
                pipeline_version=self.VERSION,
                trigger_mode=PipelineRunTrigger.SCHEDULED,
            )

            final_run_count = PipelineRun.objects.filter(pipeline=self.PIPELINE).count()
            self.assertEqual(final_run_count, initial_run_count + 1)

    def test_scheduled_run_allowed_when_previous_run_failed(self):
        PipelineRun.objects.create(
            pipeline=self.PIPELINE,
            pipeline_version=self.VERSION,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.FAILED,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(
                pipeline=self.PIPELINE
            ).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertFalse(should_skip)

            self.PIPELINE.run(
                user=None,
                pipeline_version=self.VERSION,
                trigger_mode=PipelineRunTrigger.SCHEDULED,
            )

            final_run_count = PipelineRun.objects.filter(pipeline=self.PIPELINE).count()
            self.assertEqual(final_run_count, initial_run_count + 1)

    def test_scheduled_run_allowed_when_no_previous_runs(self):
        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(
                pipeline=self.PIPELINE
            ).count()
            self.assertEqual(initial_run_count, 0)

            should_skip = PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertFalse(should_skip)

            self.PIPELINE.run(
                user=None,
                pipeline_version=self.VERSION,
                trigger_mode=PipelineRunTrigger.SCHEDULED,
            )

            final_run_count = PipelineRun.objects.filter(pipeline=self.PIPELINE).count()
            self.assertEqual(final_run_count, 1)
