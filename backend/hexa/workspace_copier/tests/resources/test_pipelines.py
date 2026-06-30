from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from slugify import slugify

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.pipelines import (
    PipelinesCopier,
    _assign_target_codes,
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
    @patch("hexa.workspace_copier.resources.pipelines._list_target_codes")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_pipelines")
    def test_creates_new_pipeline(
        self,
        mock_list,
        mock_target_codes,
        mock_detail,
        mock_create,
        mock_upload,
        mock_update,
    ):
        mock_list.return_value = [("pid-1", "my-pipeline", "My Pipeline")]
        mock_target_codes.return_value = set()  # nothing on target yet
        mock_detail.return_value = {"type": "zipFile", "name": "My Pipeline"}
        mock_create.return_value = ("tgt-pid", "my-pipeline")
        mock_upload.return_value = (["v1"], None)

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.created, [("my-pipeline", ["v1"])])
        mock_update.assert_called_once()

    @patch("hexa.workspace_copier.resources.pipelines._list_target_codes")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_pipelines")
    def test_skips_existing_pipeline(self, mock_list, mock_target_codes):
        mock_list.return_value = [("pid-1", "my-pipeline", "My Pipeline")]
        # slugify("My Pipeline") == "my-pipeline" is already on the target.
        mock_target_codes.return_value = {"my-pipeline"}

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.skipped, ["my-pipeline"])
        self.assertEqual(self.result.pipelines.created, [])

    @patch("hexa.workspace_copier.resources.pipelines._list_target_codes")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_pipelines")
    def test_same_named_source_pipelines_are_both_copied(
        self, mock_list, mock_target_codes
    ):
        # Two source pipelines share the name "DHIS2 Tracker Programs". The
        # second must not be dropped as "already existing": we disambiguate the
        # name so each gets a distinct, predictable target code.
        mock_list.return_value = [
            ("pid-1", "dhis2-tracker-programs-64e0a8", "DHIS2 Tracker Programs"),
            ("pid-2", "dhis2-tracker-programs", "DHIS2 Tracker Programs"),
        ]
        mock_target_codes.return_value = set()  # fresh workspace

        with (
            patch(
                "hexa.workspace_copier.resources.pipelines._fetch_source_detail",
                return_value={"type": "zipFile", "name": "DHIS2 Tracker Programs"},
            ),
            patch(
                "hexa.workspace_copier.resources.pipelines._create_on_target",
                side_effect=lambda _client, _slug, _detail, name: (
                    f"tgt-{name}",
                    slugify(name),
                ),
            ) as mock_create,
            patch(
                "hexa.workspace_copier.resources.pipelines._upload_versions",
                return_value=([], None),
            ),
            patch("hexa.workspace_copier.resources.pipelines._update_settings"),
        ):
            PipelinesCopier().copy(
                self.source, self.target, self.result, NullReporter()
            )

        self.assertEqual(self.result.pipelines.skipped, [])
        self.assertEqual(
            self.result.pipelines.created,
            [("dhis2-tracker-programs", []), ("dhis2-tracker-programs-2", [])],
        )
        # The disambiguated name is what gets sent to the target.
        sent_names = [call.args[3] for call in mock_create.call_args_list]
        self.assertEqual(
            sent_names, ["DHIS2 Tracker Programs", "DHIS2 Tracker Programs (2)"]
        )

    @patch("hexa.workspace_copier.resources.pipelines._list_target_codes")
    @patch("hexa.workspace_copier.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_pipelines")
    def test_notebook_without_path_is_skipped_with_warning(
        self, mock_list, mock_detail, mock_target_codes
    ):
        mock_list.return_value = [("pid-1", "nb", "nb")]
        mock_target_codes.return_value = set()
        mock_detail.return_value = {"type": "notebook", "notebookPath": None}

        PipelinesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.pipelines.skipped, ["nb"])
        self.assertTrue(
            any("notebookPath" in w for w in self.result.pipelines.warnings)
        )

    @patch("hexa.workspace_copier.resources.pipelines._list_target_codes")
    @patch("hexa.workspace_copier.resources.pipelines._create_on_target")
    @patch("hexa.workspace_copier.resources.pipelines._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.pipelines._list_source_pipelines")
    def test_failed_pipeline_is_recorded_and_does_not_abort(
        self, mock_list, mock_detail, mock_create, mock_target_codes
    ):
        mock_list.return_value = [
            ("pid-1", "bad-one", "bad-one"),
            ("pid-2", "good-one", "good-one"),
        ]
        mock_target_codes.return_value = set()
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
