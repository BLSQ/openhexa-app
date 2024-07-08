from unittest import mock
from uuid import uuid4

from django.test import RequestFactory

from hexa.core.analytics import track, track_user
from hexa.core.test import TestCase
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRunTrigger
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class AnalyticsTest(TestCase):
    @classmethod
    @mock_gcp_storage
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
        cls.factory = RequestFactory()

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_event_user_no_token(self, mock_mixpanel):
        with self.settings(
            MIXPANEL_TOKEN=None,
        ):
            self.client.force_login(self.USER)
            event = "test_event"
            properties = {"prop_1": "value_1"}

            request = self.factory.post("/login")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            request.user = self.USER

            track(request, event, properties)
            mock_mixpanel.assert_not_called()

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_user_analytics_not_enabled(
        self,
        mock_mixpanel,
    ):
        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance

        self.USER.analytics_enabled = False
        self.USER.save()

        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            request = self.factory.post("/dataset")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            request.user = self.USER

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": str(uuid4()),
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(request, event, properties)
            mock_mixpanel_instance.assert_not_called()

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_user_analytics_enabled(
        self,
        mock_mixpanel,
    ):
        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance
        mixpanel_token = "token"

        self.USER.analytics_enabled = True
        self.USER.save()

        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            request = self.factory.post("/login")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            request.user = self.USER

            track(request, "login")

            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=str(self.USER.id),
                event_name="login",
                properties={
                    "$browser": "Chrome",
                    "$device": "Mac",
                    "$os": "Mac OS X",
                    "ip": "127.0.0.1",
                },
            )

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_pipelinerun_user_exist(
        self,
        mock_mixpanel,
    ):
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
            }

            request = self.factory.post("/dataset")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            request.user = pipeline_run_user

            track(request, event, properties)

            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=str(self.USER.id), event_name=event, properties=properties
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
        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            pipeline_run = self.PIPELINE.run(
                user=None,
                pipeline_version=self.PIPELINE.last_version,
                trigger_mode=PipelineRunTrigger.MANUAL,
                config={},
            )
            pipeline_run_user = PipelineRunUser(pipeline_run=pipeline_run)

            request = self.factory.post("/dataset")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            request.user = pipeline_run_user

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": str(uuid4()),
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(request, event, properties)

            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=None, event_name=event, properties=properties
            )

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_track_pipelinerun_no_user(
        self,
        mock_mixpanel,
    ):
        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance
        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            self.PIPELINE.run(
                user=None,
                pipeline_version=self.PIPELINE.last_version,
                trigger_mode=PipelineRunTrigger.MANUAL,
                config={},
            )

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": str(uuid4()),
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(None, event, properties)
            mock_mixpanel_instance.track.assert_called_once_with(
                distinct_id=None, event_name=event, properties=properties
            )

    @mock.patch("hexa.core.analytics.Mixpanel")
    def test_create_user_profile(
        self,
        mock_mixpanel,
    ):
        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance
        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            track_user(self.USER)

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
