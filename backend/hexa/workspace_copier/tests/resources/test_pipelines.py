from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.pipelines import (
    PipelinesCopier,
    _upload_versions,
)
from hexa.workspace_copier.results import CopyResult, PipelinesResult
from hexa.workspace_copier.transport import GraphQLError


class PipelinesCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = CopyResult()

    @patch("hexa.workspace_copier.resources.pipelines._update_settings")
    @patch("hexa.workspace_copier.resources.pipelines._upload_versions")
    @patch("hexa.workspace_copier.resources.pipelines._create_on_target")
    @patch("hexa.workspace_copier.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_ids")
    def test_creates_new_pipeline(
        self, mock_ids, mock_detail, mock_create, mock_upload, mock_update
    ):
        mock_ids.return_value = [("pid-1", "my-pipeline")]
        self.target.client.pipeline.return_value = None  # not on target yet
        mock_detail.return_value = {"type": "zipFile", "name": "My Pipeline"}
        mock_create.return_value = ("tgt-pid", "my-pipeline")
        mock_upload.return_value = (["v1"], None)

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.created, [("my-pipeline", ["v1"])])
        mock_update.assert_called_once()

    @patch("hexa.workspace_copier.resources.pipelines._list_source_ids")
    def test_skips_existing_pipeline(self, mock_ids):
        mock_ids.return_value = [("pid-1", "my-pipeline")]
        self.target.client.pipeline.return_value = MagicMock()  # already exists

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.skipped, ["my-pipeline"])
        self.assertEqual(self.result.pipelines.created, [])

    @patch("hexa.workspace_copier.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_ids")
    def test_notebook_without_path_is_skipped_with_warning(self, mock_ids, mock_detail):
        mock_ids.return_value = [("pid-1", "nb")]
        self.target.client.pipeline.return_value = None
        mock_detail.return_value = {"type": "notebook", "notebookPath": None}

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.skipped, ["nb"])
        self.assertTrue(
            any("notebookPath" in w for w in self.result.pipelines.warnings)
        )

    @patch("hexa.workspace_copier.resources.pipelines._create_on_target")
    @patch("hexa.workspace_copier.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_ids")
    def test_failed_pipeline_is_recorded_and_does_not_abort(
        self, mock_ids, mock_detail, mock_create
    ):
        mock_ids.return_value = [("pid-1", "bad-one"), ("pid-2", "good-one")]
        self.target.client.pipeline.return_value = None
        mock_detail.side_effect = [
            {"type": "notebook", "notebookPath": "nb.ipynb"},
            {"type": "notebook", "notebookPath": "nb.ipynb"},
        ]
        mock_create.side_effect = [
            GraphQLError("createPipeline failed for 'bad-one': FILE_NOT_FOUND"),
            ("tgt-pid", "good-one"),
        ]

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.failed, ["bad-one"])
        self.assertEqual(self.result.pipelines.created, [("good-one", [])])
        self.assertTrue(any("bad-one" in w for w in self.result.pipelines.warnings))

    def test_local_endpoint_not_yet_implemented(self):
        with self.assertRaises(NotImplementedError):
            PipelinesCopier().copy(
                Endpoint.local("src"), self.target, self.result, NullReporter()
            )


class UploadVersionsTest(SimpleTestCase):
    @patch("hexa.workspace_copier.resources.pipelines._upload_version")
    def test_scheduled_version_binds_across_source_numbering_gaps(self, mock_upload):
        # Source has a gap (versions 2-4 deleted); the scheduled version is the
        # source's v5. The target re-numbers uploads sequentially from 1, so a
        # number-based match would never bind. The match must follow source id.
        detail = {
            "scheduledPipelineVersion": {"id": "sv-5", "versionNumber": 5},
            "versions": [
                {"id": "sv-1", "versionNumber": 1},
                {"id": "sv-5", "versionNumber": 5},
            ],
        }
        mock_upload.side_effect = [
            {"id": "tv-a", "versionName": "v1", "versionNumber": 1},
            {"id": "tv-b", "versionName": "v2", "versionNumber": 2},
        ]

        uploaded_names, scheduled_version_id = _upload_versions(
            MagicMock(), "tgt", "my-pipeline", detail, False, PipelinesResult()
        )

        self.assertEqual(uploaded_names, ["v1", "v2"])
        self.assertEqual(scheduled_version_id, "tv-b")

    @patch("hexa.workspace_copier.resources.pipelines._upload_version")
    def test_no_scheduled_version_leaves_binding_unset(self, mock_upload):
        detail = {
            "scheduledPipelineVersion": None,
            "versions": [{"id": "sv-1", "versionNumber": 1}],
        }
        mock_upload.return_value = {
            "id": "tv-a",
            "versionName": "v1",
            "versionNumber": 1,
        }

        _, scheduled_version_id = _upload_versions(
            MagicMock(), "tgt", "my-pipeline", detail, False, PipelinesResult()
        )

        self.assertIsNone(scheduled_version_id)
