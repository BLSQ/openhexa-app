from datetime import datetime, timedelta
from unittest import mock

from django.test import RequestFactory
from mixpanel import Mixpanel
from mixpanel_async import AsyncBufferedConsumer

from hexa.analytics.api import set_user_properties, track
from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline, PipelineRunTrigger
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class AnalyticsTest(TestCase):
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
        cls.factory = RequestFactory()

    @mock.patch("hexa.analytics.api.Mixpanel")
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

            track(request, event, properties, user=self.USER)
            mock_mixpanel.assert_not_called()

    @mock.patch("hexa.analytics.api.Mixpanel")
    def test_track_user_analytics_not_enabled(
        self,
        mock_mixpanel,
    ):
        mock_mixpanel_instance = mock.MagicMock()
        mock_mixpanel.return_value = mock_mixpanel_instance

        self.USER.analytics_enabled = False
        self.USER.save()

        mixpanel_token = "token"

        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            request = self.factory.post("/dataset")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"

            event = "dataset_version_created"
            properties = {
                "dataset_version": "version",
                "dataset_id": "slug",
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(request, event, properties, user=self.USER)
            mock_mixpanel_instance.assert_not_called()

    @mock.patch("hexa.analytics.api.mixpanel")
    def test_track_user_analytics_enabled(
        self,
        mock_mixpanel,
    ):
        mixpanel_token = "token"

        self.USER.analytics_enabled = True
        self.USER.save()
        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            request = self.factory.post("/login")
            request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            request.META["REMOTE_ADDR"] = "127.0.0.1"

            track(request, "login", user=self.USER)
            mock_mixpanel.track.assert_called_once_with(
                distinct_id=str(self.USER.id),
                event_name="login",
                properties={
                    "$browser": "Chrome",
                    "$device": "Mac",
                    "$os": "Mac OS X",
                    "ip": "127.0.0.1",
                },
            )

    @mock.patch("hexa.analytics.api.mixpanel")
    def test_track_pipelinerun_no_user(
        self,
        mock_mixpanel,
    ):
        mixpanel_token = "token"

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
                "dataset_id": "slug",
                "creation_source": "SDK",
                "workspace": self.WORKSPACE.slug,
            }

            track(None, event, properties)
            mock_mixpanel.track.assert_called_once_with(
                distinct_id=None,
                event_name="dataset_version_created",
                properties={
                    "dataset_version": "version",
                    "dataset_id": "slug",
                    "creation_source": "SDK",
                    "workspace": self.WORKSPACE.slug,
                },
            )

    @mock.patch("hexa.analytics.api.mixpanel")
    def test_create_user_profile(
        self,
        mock_mixpanel,
    ):
        mixpanel_token = "token"

        with self.settings(MIXPANEL_TOKEN=mixpanel_token):
            set_user_properties(self.USER)

            mock_mixpanel.people_set.assert_called_once_with(
                distinct_id=str(self.USER.id),
                properties={
                    "$email": self.USER.email,
                    "$name": self.USER.display_name,
                    "is_staff": self.USER.is_staff,
                    "is_superuser": self.USER.is_superuser,
                    "features_flag": [],
                },
            )


class AsyncMixpanelTest(TestCase):
    """
    Mixpanel team proposes to use the AsyncBufferedConsumer (from mixpanel-py-async) to queue events and send them asynchronously.
    This test suite ensures, through sanity checks, that the open-source and community-maintained AsyncBufferedConsumer implementation works as expected.
    """

    @mock.patch("mixpanel_async.AsyncBufferedConsumer._sync_flush")
    def test_async_mixpanel_queues_events(self, mock_sync_flush):
        consumer = AsyncBufferedConsumer(request_timeout=4, flush_first=False)
        mixpanel = Mixpanel(token="dummy_token", consumer=consumer)

        for i in range(3):
            mixpanel.track("event", "event_name", {"prop": f"value{i}"})

        self.assertEqual(len(consumer._async_buffers.get("events")), 3)
        consumer.flush()
        self.assertEqual(len(consumer._async_buffers.get("events")), 0)
        self.assertEqual(len(consumer._buffers.get("events")), 3)
        mock_sync_flush.assert_called_once()

    @mock.patch("mixpanel_async.AsyncBufferedConsumer._sync_flush")
    @mock.patch("mixpanel_async.async_buffered_consumer.datetime")
    def test_async_mixpanel_events_sent_without_flush(
        self, mock_datetime, mock_sync_flush
    ):
        initial_time = datetime(1995, 11, 6, 12, 50, 33)
        mock_datetime.now.return_value = initial_time
        flush_after = timedelta(seconds=10)
        consumer = AsyncBufferedConsumer(
            request_timeout=4, flush_first=False, flush_after=flush_after
        )
        mixpanel = Mixpanel(token="dummy_token", consumer=consumer)

        for i in range(3):
            mixpanel.track("event", "event_name", {"prop": f"value{i+1}"})

        # Simulate a bit more than the flush_after time passing
        mock_datetime.now.return_value = (
            initial_time + flush_after + timedelta(microseconds=1)
        )

        self.assertEqual(
            len(consumer._async_buffers.get("events")), 3
        )  # Flush happens only when a new event is tracked

        mixpanel.track("event", "event_name", {"prop": "value4"})

        self.assertEqual(len(consumer._async_buffers.get("events")), 0)
        self.assertEqual(len(consumer._buffers.get("events")), 4)
        mock_sync_flush.assert_called_once()
