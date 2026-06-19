from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.resources import datasets as datasets_module
from hexa.workspace_duplicator.resources.datasets import DatasetsCopier
from hexa.workspace_duplicator.results import (
    DatasetsResult,
    DuplicationResult,
    format_summary,
)
from hexa.workspace_duplicator.transport import GraphQLError

MODULE = "hexa.workspace_duplicator.resources.datasets"


def _dataset(slug, owner="src", **extra):
    return {
        "id": f"id-{slug}",
        "slug": slug,
        "name": slug.upper(),
        "description": "",
        "workspace": {"slug": owner} if owner else None,
        **extra,
    }


def _version(name):
    return {"id": f"v-{name}", "name": name, "changelog": ""}


def _file(filename):
    return {"id": f"f-{filename}", "filename": filename, "contentType": "text/csv"}


class DatasetsCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = DuplicationResult()

    @patch(f"{MODULE}.upload")
    @patch(f"{MODULE}.download")
    @patch(f"{MODULE}._list_version_files")
    @patch(f"{MODULE}._create_version")
    @patch(f"{MODULE}._list_versions")
    @patch(f"{MODULE}._create_dataset")
    @patch(f"{MODULE}._list_owned_datasets")
    @patch(f"{MODULE}._list_workspace_dataset_slugs")
    def test_copies_dataset_with_versions_and_files(
        self,
        mock_target_slugs,
        mock_owned,
        mock_create_dataset,
        mock_list_versions,
        mock_create_version,
        mock_list_files,
        mock_download,
        mock_upload,
    ):
        mock_target_slugs.return_value = set()
        mock_owned.return_value = [_dataset("survey")]
        mock_create_dataset.return_value = ("tid", "survey")
        mock_list_versions.return_value = [_version("v1"), _version("v2")]
        mock_create_version.side_effect = ["tv1", "tv2"]
        mock_list_files.side_effect = [[_file("a.csv")], [_file("b.csv")]]
        mock_download.return_value = b"data"

        DatasetsCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.datasets.created, [("survey", ["v1", "v2"])])
        self.assertEqual(self.result.datasets.files_copied, 2)
        self.assertEqual(self.result.datasets.failed, [])
        # Files uploaded to the version that was just created (latest).
        self.assertEqual(
            [call.args[1] for call in mock_upload.call_args_list], ["tv1", "tv2"]
        )

    @patch(f"{MODULE}._create_dataset")
    @patch(f"{MODULE}._list_owned_datasets")
    @patch(f"{MODULE}._list_workspace_dataset_slugs")
    def test_skips_dataset_already_on_target(
        self, mock_target_slugs, mock_owned, mock_create_dataset
    ):
        mock_target_slugs.return_value = {"survey"}
        mock_owned.return_value = [_dataset("survey")]

        DatasetsCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.datasets.skipped, ["survey"])
        self.assertEqual(self.result.datasets.created, [])
        mock_create_dataset.assert_not_called()

    @patch(f"{MODULE}._list_versions")
    @patch(f"{MODULE}._create_dataset")
    @patch(f"{MODULE}._list_owned_datasets")
    @patch(f"{MODULE}._list_workspace_dataset_slugs")
    def test_failed_dataset_is_recorded_and_loop_continues(
        self, mock_target_slugs, mock_owned, mock_create_dataset, mock_list_versions
    ):
        mock_target_slugs.return_value = set()
        mock_owned.return_value = [_dataset("bad"), _dataset("good")]
        mock_create_dataset.side_effect = [
            GraphQLError("boom"),
            ("tid", "good"),
        ]
        mock_list_versions.return_value = []

        DatasetsCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.datasets.failed, ["bad"])
        self.assertEqual(self.result.datasets.created, [("good", [])])

    @patch(f"{MODULE}.upload")
    @patch(f"{MODULE}.download")
    @patch(f"{MODULE}._list_version_files")
    @patch(f"{MODULE}._create_version")
    @patch(f"{MODULE}._list_versions")
    @patch(f"{MODULE}._create_dataset")
    @patch(f"{MODULE}._list_owned_datasets")
    @patch(f"{MODULE}._list_workspace_dataset_slugs")
    def test_failed_file_is_warned_and_dataset_still_created(
        self,
        mock_target_slugs,
        mock_owned,
        mock_create_dataset,
        mock_list_versions,
        mock_create_version,
        mock_list_files,
        mock_download,
        mock_upload,
    ):
        mock_target_slugs.return_value = set()
        mock_owned.return_value = [_dataset("survey")]
        mock_create_dataset.return_value = ("tid", "survey")
        mock_list_versions.return_value = [_version("v1")]
        mock_create_version.return_value = "tv1"
        mock_list_files.return_value = [_file("bad.csv"), _file("ok.csv")]
        mock_download.side_effect = [GraphQLError("boom"), b"ok"]

        DatasetsCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.datasets.created, [("survey", ["v1"])])
        self.assertEqual(self.result.datasets.files_copied, 1)
        self.assertTrue(any("bad.csv" in w for w in self.result.datasets.warnings))

    @patch(f"{MODULE}._list_versions")
    @patch(f"{MODULE}._create_dataset")
    @patch(f"{MODULE}._list_owned_datasets")
    @patch(f"{MODULE}._list_workspace_dataset_slugs")
    def test_records_server_assigned_slug(
        self, mock_target_slugs, mock_owned, mock_create_dataset, mock_list_versions
    ):
        mock_target_slugs.return_value = set()
        mock_owned.return_value = [_dataset("survey")]
        mock_create_dataset.return_value = ("tid", "survey-x7a2")
        mock_list_versions.return_value = []

        DatasetsCopier().copy(self.source, self.target, self.result)

        self.assertEqual(self.result.datasets.created, [("survey-x7a2", [])])
        self.assertEqual(self.result.datasets.warnings, [])

    def test_local_endpoint_not_yet_implemented(self):
        with self.assertRaises(NotImplementedError):
            DatasetsCopier().copy(Endpoint.local("src"), self.target, self.result)


class ListOwnedDatasetsTest(SimpleTestCase):
    @patch(f"{MODULE}.gql")
    def test_keeps_only_datasets_owned_by_source(self, mock_gql):
        mock_gql.return_value = {
            "workspace": {
                "datasets": {
                    "totalPages": 1,
                    "items": [
                        {"dataset": _dataset("owned", owner="src")},
                        {"dataset": _dataset("shared-in", owner="other")},
                        {"dataset": _dataset("orphan", owner=None)},
                    ],
                }
            }
        }

        owned = datasets_module._list_owned_datasets(MagicMock(), "src")

        self.assertEqual([d["slug"] for d in owned], ["owned"])

    @patch(f"{MODULE}.gql")
    def test_missing_workspace_raises(self, mock_gql):
        mock_gql.return_value = {"workspace": None}

        with self.assertRaises(GraphQLError):
            datasets_module._list_owned_datasets(MagicMock(), "src")


class DatasetsSummaryTest(SimpleTestCase):
    def test_summary_lists_created_skipped_and_failed(self):
        result = DuplicationResult(workspace_name="WS", workspace_slug="ws")
        result.datasets = DatasetsResult(
            created=[("survey", ["v1", "v2"])],
            skipped=["old"],
            failed=["broken"],
            files_copied=3,
            warnings=["something off"],
        )

        summary = format_summary(result)

        self.assertIn("Datasets created: 1 (3 file(s) copied)", summary)
        self.assertIn("* survey", summary)
        self.assertIn("- v1", summary)
        self.assertIn("Datasets skipped (already existed): 1", summary)
        self.assertIn("Datasets that could NOT be migrated", summary)
        self.assertIn("something off", summary)


class ListVersionsTest(SimpleTestCase):
    @patch(f"{MODULE}.gql")
    def test_returns_versions_oldest_first(self, mock_gql):
        # API returns newest-first; the copier must recreate oldest-first.
        mock_gql.return_value = {
            "dataset": {
                "versions": {
                    "totalPages": 1,
                    "items": [_version("v3"), _version("v2"), _version("v1")],
                }
            }
        }

        versions = datasets_module._list_versions(MagicMock(), "ds-id")

        self.assertEqual([v["name"] for v in versions], ["v1", "v2", "v3"])
