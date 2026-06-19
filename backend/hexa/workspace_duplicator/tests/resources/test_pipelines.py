from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources.pipelines import PipelinesCopier
from hexa.workspace_duplicator.results import DuplicationResult


class PipelinesCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = DuplicationResult()

    @patch("hexa.workspace_duplicator.resources.pipelines._update_settings")
    @patch("hexa.workspace_duplicator.resources.pipelines._upload_versions")
    @patch("hexa.workspace_duplicator.resources.pipelines._create_on_target")
    @patch("hexa.workspace_duplicator.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_duplicator.resources.pipelines._list_source_ids")
    def test_creates_new_pipeline(
        self, mock_ids, mock_detail, mock_create, mock_upload, mock_update
    ):
        mock_ids.return_value = [("pid-1", "my-pipeline")]
        self.target.client.pipeline.return_value = None  # not on target yet
        mock_detail.return_value = {"type": "zipFile", "name": "My Pipeline"}
        mock_create.return_value = ("tgt-pid", "my-pipeline")
        mock_upload.return_value = (["v1"], None)

        PipelinesCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.pipelines.created, [("my-pipeline", ["v1"])])
        mock_update.assert_called_once()

    @patch("hexa.workspace_duplicator.resources.pipelines._list_source_ids")
    def test_skips_existing_pipeline(self, mock_ids):
        mock_ids.return_value = [("pid-1", "my-pipeline")]
        self.target.client.pipeline.return_value = MagicMock()  # already exists

        PipelinesCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.pipelines.skipped, ["my-pipeline"])
        self.assertEqual(self.result.pipelines.created, [])

    @patch("hexa.workspace_duplicator.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_duplicator.resources.pipelines._list_source_ids")
    def test_notebook_without_path_is_skipped_with_warning(self, mock_ids, mock_detail):
        mock_ids.return_value = [("pid-1", "nb")]
        self.target.client.pipeline.return_value = None
        mock_detail.return_value = {"type": "notebook", "notebookPath": None}

        PipelinesCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.pipelines.skipped, ["nb"])
        self.assertTrue(
            any("notebookPath" in w for w in self.result.pipelines.warnings)
        )

    def test_local_endpoint_not_yet_implemented(self):
        with self.assertRaises(NotImplementedError):
            PipelinesCopier().copy(Endpoint.local("src"), self.target, self.result)
