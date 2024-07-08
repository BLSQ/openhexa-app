from datetime import datetime
from unittest import mock
from uuid import uuid4

from hexa.core.analytics import mixpanel_consumer, track
from hexa.core.test import TestCase
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRunTrigger
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class AnalyticsTest(TestCase):
    def setUp(self):
        # flush the buffer before each test
        mixpanel_consumer.flush()

    @classmethod
    def setUpTestData(cls):
        cls.USER: User = User.objects.create_user(
            "user@bluesquarehub.com", "user", analytics_enabled=True, is_superuser=True
        )

        cls.WORKSPACE: Workspace = Workspace.objects.create_if_has_perm(
            cls.USER,
            name="Sandbox",
            description="This is a sandbox workspace ",
            countries=[{"code": "AL"}],
        )
        cls.PIPELINE: Pipeline = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
        )
        cls.PIPELINE.upload_new_version(
            cls.USER, zipfile=b"", parameters=[], name="Version"
        )

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_event_user_no_token(self, mock_mixpanel):
        with self.settings(
            MIXPANEL_TOKEN=None,
        ):
            event = "test_event"
            properties = {"prop_1": "value_1"}
            mock_request = mock.MagicMock()

            track(self.USER, event, properties, mock_request)
            mock_mixpanel.assert_not_called()

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_pipelinerun_user_exist(
        self,
        mock_datetime,
        mock_mixpanel,
    ):
        now = datetime.now()
        mock_datetime.now.return_value = now
        with self.settings(MIXPANEL_TOKEN="mixpanel_token"):
            mock_mixpanel_instance = mock.MagicMock()
            mock_mixpanel.return_value = mock_mixpanel_instance

            pipeline_run = self.PIPELINE.run(
                user=self.USER,
                pipeline_version=self.PIPELINE.last_version,
                trigger_mode=PipelineRunTrigger.MANUAL,
                config={},
            )
            pipeline_run_user = PipelineRunUser(pipeline_run=pipeline_run)

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": str(uuid4()),
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
                "timestamp": now.timestamp(),
            }

            track(pipeline_run_user, event, properties)

            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=str(self.USER.id), event_name=event, properties=properties
            )
            mock_mixpanel_instance.people_set_once.assert_called_once_with(
                distinct_id=str(self.USER.id),
                properties={
                    "$email": self.USER.email,
                    "$name": self.USER.display_name,
                    "staff_status": self.USER.is_staff,
                    "superuser_status": self.USER.is_superuser,
                    "email_domain": "bluesquarehub.com",
                    "features_flag": [],
                },
            )

    @mock.patch("hexa.core.analytics.Mixpanel")
    @mock.patch("hexa.core.analytics.datetime")
    def test_track_user_analytics_not_enabled(
        self,
        mock_datetime,
        mock_mixpanel,
    ):
        now = datetime.now()
        mock_datetime.now.return_value = now

        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance

        self.USER.analytics_enabled = False
        self.USER.save()

        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            pipeline_run = self.PIPELINE.run(
                user=self.USER,
                pipeline_version=self.PIPELINE.last_version,
                trigger_mode=PipelineRunTrigger.MANUAL,
                config={},
            )
            pipeline_run_user = PipelineRunUser(pipeline_run=pipeline_run)

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": str(uuid4()),
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(pipeline_run_user, event, properties)
            mock_mixpanel_instance.assert_not_called()

    @mock.patch("hexa.core.analytics.Mixpanel")
    @mock.patch("hexa.core.analytics.datetime")
    def test_track_user_analytics_enabled(
        self,
        mock_datetime,
        mock_mixpanel,
    ):
        now = datetime.now()
        mock_datetime.now.return_value = now

        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance
        mixpanel_token = "token"

        self.USER.analytics_enabled = True
        self.USER.save()

        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            track(self.USER, "login")
            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=str(self.USER.id),
                event_name="login",
                properties={"timestamp": now.timestamp()},
            )
            mock_mixpanel_instance.people_set_once.assert_called_once_with(
                distinct_id=str(self.USER.id),
                properties={
                    "$email": self.USER.email,
                    "$name": self.USER.display_name,
                    "staff_status": self.USER.is_staff,
                    "superuser_status": self.USER.is_superuser,
                    "email_domain": "bluesquarehub.com",
                    "features_flag": [],
                },
            )

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_pipelinerun_user_none(
        self,
        mock_mixpanel,
    ):
        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance
        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token), mock.patch.object(
            mixpanel_consumer, "flush"
        ):
            pipeline_run = self.PIPELINE.run(
                user=None,
                pipeline_version=self.PIPELINE.last_version,
                trigger_mode=PipelineRunTrigger.MANUAL,
                config={},
            )
            pipeline_run_user = PipelineRunUser(pipeline_run=pipeline_run)

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": str(uuid4()),
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(pipeline_run_user, event, properties)

            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=None, event_name=event, properties=properties
            )
