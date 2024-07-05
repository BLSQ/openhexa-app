import json
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

    def test_track_user_analytics_not_enabled(
        self,
    ):
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
            self.assertEqual(len(mixpanel_consumer._buffers["events"]), 0)
            self.assertEqual(len(mixpanel_consumer._buffers["people"]), 0)

    def test_track_user_analytics_enabled(
        self,
    ):
        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token), mock.patch.object(
            mixpanel_consumer, "flush"
        ) as mocked_flush:
            mock_request = mock.Mock()
            mock_request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            mock_request.META = {"REMOTE_ADDR": "127.0.0.1"}

            track(self.USER, "login", request=mock_request)

            self.assertEqual(len(mixpanel_consumer._buffers["events"]), 1)
            self.assertEqual(len(mixpanel_consumer._buffers["people"]), 1)

            mixpanel_args = json.loads(mixpanel_consumer._buffers["events"][0])

            self.assertTrue(mixpanel_args["event"], "login")
            self.assertTrue(
                mixpanel_args["properties"]["distinct_id"], str(self.USER.id)
            )
            self.assertTrue(mixpanel_args["properties"]["$device"], "Mac")
            self.assertTrue(mixpanel_args["properties"]["$browser"], "Chrome")
            self.assertTrue(mixpanel_args["properties"]["ip"], "127.0.0.1")

            mocked_flush.assert_not_called()

    def test_track_pipelinerun_user_exist(
        self,
    ):
        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token), mock.patch.object(
            mixpanel_consumer, "flush"
        ) as mocked_flush:
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

            self.assertEqual(len(mixpanel_consumer._buffers["events"]), 1)
            self.assertEqual(len(mixpanel_consumer._buffers["people"]), 1)
            mocked_flush.assert_not_called()

            mixpanel_args = json.loads(mixpanel_consumer._buffers["events"][0])
            self.assertTrue(
                set(properties.items()).issubset(
                    set(mixpanel_args["properties"].items())
                )
            )

    def test_track_pipelinerun_user_none(
        self,
    ):
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
            self.assertEqual(len(mixpanel_consumer._buffers["events"]), 1)
            self.assertEqual(len(mixpanel_consumer._buffers["people"]), 0)

            mixpanel_args = json.loads(mixpanel_consumer._buffers["events"][0])

            self.assertTrue(mixpanel_args["event"], "login")
            self.assertEqual(mixpanel_args["properties"]["distinct_id"], None)

    def test_track_pipelinerun_user_with_request(
        self,
    ):
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
            mock_request = mock.Mock()
            mock_request.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            mock_request.META = {"REMOTE_ADDR": "127.0.0.1"}

            track(pipeline_run_user, event, properties, mock_request)

            self.assertEqual(len(mixpanel_consumer._buffers["events"]), 1)
            self.assertEqual(len(mixpanel_consumer._buffers["people"]), 0)

            mixpanel_args = json.loads(mixpanel_consumer._buffers["events"][0])

            self.assertTrue(mixpanel_args["event"], "login")
            self.assertEqual(mixpanel_args["properties"]["distinct_id"], None)
            self.assertFalse(
                all(
                    [
                        f in mixpanel_args["properties"]
                        for f in ["$browser", "$device", "$os", "ip"]
                    ]
                ),
            )

    def test_track_pipelinerun_user_flushed_buffer(
        self,
    ):
        mixpanel_token = "token"
        # mock the flush method of the BufferedConsumer
        with self.settings(MIXPANEL_TOKEN=mixpanel_token), mock.patch.object(
            mixpanel_consumer, "_flush_endpoint"
        ) as mocked_flush_endpoint, mock.patch.object(
            mixpanel_consumer, "_max_size", 2
        ):
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
            self.assertEqual(len(mixpanel_consumer._buffers["events"]), 1)
            self.assertEqual(len(mixpanel_consumer._buffers["people"]), 1)

            mocked_flush_endpoint.assert_not_called()

            # second call to flush the buffer endpoints (events,people)
            track(pipeline_run_user, event, properties)
            mocked_flush_endpoint.assert_called()
