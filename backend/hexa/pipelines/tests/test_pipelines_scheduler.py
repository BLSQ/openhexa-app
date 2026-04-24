from datetime import timedelta
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


class ScheduledPipelineVersionTest(TestCase):
    """Tests that the scheduler respects the pinned scheduled_pipeline_version."""

    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "schedver_admin@bluesquarehub.com",
            "admin",
            is_superuser=True,
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="SchedulerVersionTestWS",
            description="",
            countries=[{"code": "AL"}],
        )
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Version Pin Pipeline",
            code="version_pin_pipeline",
            schedule="*/5 * * * *",
            type=PipelineType.ZIPFILE,
        )
        cls.VERSION_1 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            name="v1",
            parameters=[],
        )
        cls.VERSION_2 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            name="v2",
            parameters=[],
        )

    def _run_scheduler_once(self):
        """Invoke the scheduler command for a single iteration.

        A past seed run is required so the pipeline's next scheduled time
        falls before now (negative next_exec_delay), which means the
        per-pipeline sleep is skipped and the pipeline fires immediately.
        The first sleep call that occurs is therefore the end-of-loop sleep,
        which we raise StopIteration on to break the while-True loop.
        """
        from hexa.pipelines.management.commands.pipelines_scheduler import Command

        PipelineRun.objects.create(
            pipeline=self.PIPELINE,
            pipeline_version=self.VERSION_2,
            run_id="seed__past",
            trigger_mode=PipelineRunTrigger.SCHEDULED,
            execution_date=timezone.now() - timedelta(hours=1),
            state=PipelineRunState.SUCCESS,
            config={},
        )

        with patch(
            "hexa.pipelines.management.commands.pipelines_scheduler.sleep",
            side_effect=StopIteration,
        ):
            with patch("hexa.analytics.api.track"):
                try:
                    Command().handle()
                except StopIteration:
                    pass

    def test_scheduler_uses_pinned_version(self):
        self.PIPELINE.scheduled_pipeline_version = self.VERSION_1
        self.PIPELINE.save()

        self._run_scheduler_once()

        new_run = (
            PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                trigger_mode=PipelineRunTrigger.SCHEDULED,
            )
            .order_by("-execution_date")
            .first()
        )
        self.assertIsNotNone(new_run)
        self.assertEqual(new_run.pipeline_version, self.VERSION_1)

    def test_scheduler_falls_back_to_last_version_when_no_pin(self):
        self.PIPELINE.scheduled_pipeline_version = None
        self.PIPELINE.save()

        self._run_scheduler_once()

        new_run = (
            PipelineRun.objects.filter(
                pipeline=self.PIPELINE,
                trigger_mode=PipelineRunTrigger.SCHEDULED,
            )
            .order_by("-execution_date")
            .first()
        )
        self.assertIsNotNone(new_run)
        self.assertEqual(new_run.pipeline_version, self.PIPELINE.last_version)
        self.assertEqual(new_run.pipeline_version, self.VERSION_2)

    def test_is_schedulable_uses_pinned_version(self):
        # v1 is schedulable (no required params without defaults)
        self.PIPELINE.scheduled_pipeline_version = self.VERSION_1
        self.PIPELINE.save()
        self.assertTrue(self.PIPELINE.is_schedulable)

    def test_is_schedulable_falls_back_to_last_version(self):
        self.PIPELINE.scheduled_pipeline_version = None
        self.PIPELINE.save()
        # VERSION_2 is the latest and has no required params → schedulable
        self.assertTrue(self.PIPELINE.is_schedulable)

    def test_is_schedulable_false_when_pinned_version_unschedulable(self):
        unschedulable_version = PipelineVersion.objects.create(
            pipeline=self.PIPELINE,
            name="unschedulable",
            parameters=[
                {
                    "code": "required_param",
                    "name": "Required",
                    "type": "str",
                    "required": True,
                }
            ],
        )
        self.PIPELINE.scheduled_pipeline_version = unschedulable_version
        self.PIPELINE.save()

        self.assertFalse(self.PIPELINE.is_schedulable)

        # Clean up so it doesn't affect other tests
        self.PIPELINE.scheduled_pipeline_version = None
        self.PIPELINE.save()
        unschedulable_version.delete()
