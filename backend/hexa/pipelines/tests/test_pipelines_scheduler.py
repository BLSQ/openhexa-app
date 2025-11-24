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

    def test_scheduled_run_skipped_when_queued_run_exists(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Test Pipeline",
            code="test_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.NOTEBOOK,
        )

        version = PipelineVersion.objects.create(
            pipeline=pipeline,
            name="v1",
            parameters=[],
        )

        PipelineRun.objects.create(
            pipeline=pipeline,
            pipeline_version=version,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.QUEUED,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=pipeline,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertTrue(should_skip)

            if not should_skip:
                pipeline.run(
                    user=None,
                    pipeline_version=version,
                    trigger_mode=PipelineRunTrigger.SCHEDULED,
                )

            final_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(
                final_run_count,
                initial_run_count,
            )

    def test_scheduled_run_skipped_when_running_run_exists(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Test Pipeline",
            code="test_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.NOTEBOOK,
        )

        version = PipelineVersion.objects.create(
            pipeline=pipeline,
            name="v1",
            parameters=[],
        )

        PipelineRun.objects.create(
            pipeline=pipeline,
            pipeline_version=version,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.RUNNING,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=pipeline,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertTrue(should_skip)

            if not should_skip:
                pipeline.run(
                    user=None,
                    pipeline_version=version,
                    trigger_mode=PipelineRunTrigger.SCHEDULED,
                )

            final_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(
                final_run_count,
                initial_run_count,
            )

    def test_scheduled_run_allowed_when_previous_run_completed(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Test Pipeline",
            code="test_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.NOTEBOOK,
        )

        version = PipelineVersion.objects.create(
            pipeline=pipeline,
            name="v1",
            parameters=[],
        )

        PipelineRun.objects.create(
            pipeline=pipeline,
            pipeline_version=version,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.SUCCESS,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=pipeline,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertFalse(should_skip)

            if not should_skip:
                pipeline.run(
                    user=None,
                    pipeline_version=version,
                    trigger_mode=PipelineRunTrigger.SCHEDULED,
                )

            final_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(final_run_count, initial_run_count + 1)

    def test_scheduled_run_allowed_when_previous_run_failed(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Test Pipeline",
            code="test_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.NOTEBOOK,
        )

        version = PipelineVersion.objects.create(
            pipeline=pipeline,
            name="v1",
            parameters=[],
        )

        PipelineRun.objects.create(
            pipeline=pipeline,
            pipeline_version=version,
            run_id=f"{PipelineRunTrigger.MANUAL}__1234567890",
            trigger_mode=PipelineRunTrigger.MANUAL,
            execution_date=timezone.now(),
            state=PipelineRunState.FAILED,
            config={},
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(initial_run_count, 1)

            should_skip = PipelineRun.objects.filter(
                pipeline=pipeline,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertFalse(should_skip)

            if not should_skip:
                pipeline.run(
                    user=None,
                    pipeline_version=version,
                    trigger_mode=PipelineRunTrigger.SCHEDULED,
                )

            final_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(final_run_count, initial_run_count + 1)

    def test_scheduled_run_allowed_when_no_previous_runs(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Test Pipeline",
            code="test_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.NOTEBOOK,
        )

        version = PipelineVersion.objects.create(
            pipeline=pipeline,
            name="v1",
            parameters=[],
        )

        with patch("hexa.analytics.api.track"):
            initial_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(initial_run_count, 0)

            should_skip = PipelineRun.objects.filter(
                pipeline=pipeline,
                state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
            ).exists()
            self.assertFalse(should_skip)

            if not should_skip:
                pipeline.run(
                    user=None,
                    pipeline_version=version,
                    trigger_mode=PipelineRunTrigger.SCHEDULED,
                )

            final_run_count = PipelineRun.objects.filter(pipeline=pipeline).count()
            self.assertEqual(final_run_count, 1)
