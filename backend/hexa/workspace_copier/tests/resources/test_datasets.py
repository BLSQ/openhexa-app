from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.datasets import (
    DatasetsCopier,
    _assign_target_names,
    _copy_versions,
    _list_source_datasets,
    _relative_uri,
    _select_versions,
)
from hexa.workspace_copier.results import CopyResult, DatasetsResult
from hexa.workspace_copier.transport import GraphQLError


def _detail(slug="my-dataset", **overrides):
    detail = {
        "id": "sd-1",
        "slug": slug,
        "name": slug,
        "description": "",
        "sharedWithOrganization": False,
        "latestVersion": {"id": "sv-2", "name": "v2", "changelog": ""},
    }
    detail.update(overrides)
    return detail


class DatasetsCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = CopyResult()

    @patch("hexa.workspace_copier.resources.datasets._copy_versions")
    @patch("hexa.workspace_copier.resources.datasets._apply_sharing")
    @patch("hexa.workspace_copier.resources.datasets._create_on_target")
    @patch("hexa.workspace_copier.resources.datasets._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.datasets._list_target_slugs")
    @patch("hexa.workspace_copier.resources.datasets._list_source_datasets")
    def test_creates_new_dataset(
        self,
        mock_list,
        mock_target_slugs,
        mock_detail,
        mock_create,
        mock_sharing,
        mock_versions,
    ):
        mock_list.return_value = [("sd-1", "my-dataset", "My Dataset")]
        mock_target_slugs.return_value = set()
        mock_detail.return_value = _detail()
        mock_create.return_value = ("td-1", "my-dataset")
        mock_versions.return_value = ["v2"]

        DatasetsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.datasets.created, [("my-dataset", ["v2"])])
        self.assertEqual(self.result.datasets.failed, [])
        mock_sharing.assert_called_once()

    @patch("hexa.workspace_copier.resources.datasets._list_target_slugs")
    @patch("hexa.workspace_copier.resources.datasets._list_source_datasets")
    def test_skips_existing_dataset(self, mock_list, mock_target_slugs):
        mock_list.return_value = [("sd-1", "my-dataset", "My Dataset")]
        # slugify("My Dataset") == "my-dataset" is already on the target.
        mock_target_slugs.return_value = {"my-dataset"}

        DatasetsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.datasets.skipped, ["my-dataset"])
        self.assertEqual(self.result.datasets.created, [])

    @patch("hexa.workspace_copier.resources.datasets._copy_versions")
    @patch("hexa.workspace_copier.resources.datasets._apply_sharing")
    @patch("hexa.workspace_copier.resources.datasets._create_on_target")
    @patch("hexa.workspace_copier.resources.datasets._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.datasets._list_target_slugs")
    @patch("hexa.workspace_copier.resources.datasets._list_source_datasets")
    def test_failed_dataset_is_recorded_and_does_not_abort(
        self,
        mock_list,
        mock_target_slugs,
        mock_detail,
        mock_create,
        mock_sharing,
        mock_versions,
    ):
        mock_list.return_value = [
            ("sd-1", "bad-one", "bad-one"),
            ("sd-2", "good-one", "good-one"),
        ]
        mock_target_slugs.return_value = set()
        mock_detail.side_effect = [_detail("bad-one"), _detail("good-one")]
        mock_create.side_effect = [("td-1", "bad-one"), ("td-2", "good-one")]
        mock_versions.side_effect = [
            GraphQLError("file 'a.csv' of version 'v2' failed"),
            ["v2"],
        ]

        DatasetsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.datasets.failed, ["bad-one"])
        self.assertEqual(self.result.datasets.created, [("good-one", ["v2"])])
        self.assertTrue(any("bad-one" in w for w in self.result.datasets.warnings))

    @patch("hexa.workspace_copier.resources.datasets._copy_versions")
    @patch("hexa.workspace_copier.resources.datasets._apply_sharing")
    @patch("hexa.workspace_copier.resources.datasets._create_on_target")
    @patch("hexa.workspace_copier.resources.datasets._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.datasets._list_target_slugs")
    @patch("hexa.workspace_copier.resources.datasets._list_source_datasets")
    def test_versionless_dataset_is_still_created(
        self,
        mock_list,
        mock_target_slugs,
        mock_detail,
        mock_create,
        mock_sharing,
        mock_versions,
    ):
        mock_list.return_value = [("sd-1", "empty", "empty")]
        mock_target_slugs.return_value = set()
        mock_detail.return_value = _detail("empty", latestVersion=None)
        mock_create.return_value = ("td-1", "empty")
        mock_versions.return_value = []

        DatasetsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.datasets.created, [("empty", [])])
        self.assertEqual(mock_versions.call_args.args[4], [])

    def test_local_endpoint_not_yet_implemented(self):
        with self.assertRaises(NotImplementedError):
            DatasetsCopier().copy(
                Endpoint.local("src"), self.target, self.result, NullReporter()
            )


class ListSourceDatasetsTest(SimpleTestCase):
    @patch("hexa.workspace_copier.resources.datasets.gql")
    def test_only_datasets_owned_by_the_workspace_are_listed(self, mock_gql):
        # The workspace's dataset page also lists datasets it merely has access
        # to: one owned by another workspace, one whose workspace is gone.
        mock_gql.return_value = {
            "workspace": {
                "datasets": {
                    "totalPages": 1,
                    "items": [
                        {
                            "dataset": {
                                "id": "sd-1",
                                "slug": "mine",
                                "name": "Mine",
                                "workspace": {"slug": "src"},
                            }
                        },
                        {
                            "dataset": {
                                "id": "sd-2",
                                "slug": "theirs",
                                "name": "Theirs",
                                "workspace": {"slug": "other-ws"},
                            }
                        },
                        {
                            "dataset": {
                                "id": "sd-3",
                                "slug": "orphan",
                                "name": "Orphan",
                                "workspace": None,
                            }
                        },
                    ],
                }
            }
        }

        datasets = _list_source_datasets(MagicMock(), "src")

        self.assertEqual(datasets, [("sd-1", "mine", "Mine")])


class AssignTargetNamesTest(SimpleTestCase):
    def test_same_named_datasets_get_distinct_predictable_slugs(self):
        # Two source datasets share a name. The second must not be dropped as
        # "already existing": we disambiguate the name so the target server
        # produces a slug we can predict instead of a random suffix.
        assignments = _assign_target_names(
            [
                ("sd-1", "population-a1b2c3", "Population"),
                ("sd-2", "population", "Population"),
            ]
        )

        self.assertEqual(
            assignments,
            [
                ("sd-2", "population", "Population", "population"),
                ("sd-1", "population-a1b2c3", "Population (2)", "population-2"),
            ],
        )


class SelectVersionsTest(SimpleTestCase):
    def test_default_takes_the_latest_version_only(self):
        client = MagicMock()
        versions = _select_versions(client, "sd-1", _detail(), all_versions=False)

        self.assertEqual(versions, [{"id": "sv-2", "name": "v2", "changelog": ""}])
        client.execute.assert_not_called()

    def test_default_on_a_versionless_dataset_is_empty(self):
        versions = _select_versions(
            MagicMock(), "sd-1", _detail(latestVersion=None), all_versions=False
        )

        self.assertEqual(versions, [])

    @patch("hexa.workspace_copier.resources.datasets.gql")
    def test_all_versions_are_paged_and_returned_oldest_first(self, mock_gql):
        # The API returns versions newest-first; the target only accepts files
        # for its latest version, so they have to be replayed oldest-first.
        mock_gql.side_effect = [
            {
                "dataset": {
                    "versions": {
                        "totalPages": 2,
                        "items": [
                            {"id": "sv-3", "name": "v3", "createdAt": "2024-03-01"},
                            {"id": "sv-2", "name": "v2", "createdAt": "2024-02-01"},
                        ],
                    }
                }
            },
            {
                "dataset": {
                    "versions": {
                        "totalPages": 2,
                        "items": [
                            {"id": "sv-1", "name": "v1", "createdAt": "2024-01-01"}
                        ],
                    }
                }
            },
        ]

        versions = _select_versions(MagicMock(), "sd-1", _detail(), all_versions=True)

        self.assertEqual([v["name"] for v in versions], ["v1", "v2", "v3"])


class RelativeUriTest(SimpleTestCase):
    def test_strips_the_source_dataset_and_version_prefix(self):
        file = {"uri": "sd-1/sv-2/sub/dir/data.csv", "filename": "data.csv"}

        self.assertEqual(_relative_uri(file, "sd-1", "sv-2"), "sub/dir/data.csv")

    def test_falls_back_to_filename_when_the_prefix_is_absent(self):
        file = {"uri": "unexpected/data.csv", "filename": "data.csv"}

        self.assertEqual(_relative_uri(file, "sd-1", "sv-2"), "data.csv")


class CopyVersionsTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.ds_result = DatasetsResult()

    def _copy(self, versions):
        return _copy_versions(
            self.source,
            self.target,
            "sd-1",
            "td-1",
            versions,
            self.ds_result,
            NullReporter(),
            MagicMock(),
        )

    @patch("hexa.workspace_copier.resources.datasets._transfer_file")
    @patch("hexa.workspace_copier.resources.datasets._prepare_download")
    @patch("hexa.workspace_copier.resources.datasets._list_version_files")
    @patch("hexa.workspace_copier.resources.datasets._create_version")
    def test_each_version_is_filled_before_the_next_one_is_created(
        self, mock_create, mock_files, mock_download, mock_transfer
    ):
        # A version stops accepting files as soon as a newer one exists, so the
        # order must be create v1, upload v1's files, create v2, ...
        calls = []
        mock_create.side_effect = lambda _client, _dataset_id, version: (
            calls.append(f"create {version['name']}") or f"t{version['name']}"
        )
        mock_files.side_effect = [
            [{"id": "f1", "uri": "sd-1/sv-1/a.csv", "filename": "a.csv"}],
            [{"id": "f2", "uri": "sd-1/sv-2/b.csv", "filename": "b.csv"}],
        ]
        mock_download.return_value = "https://download"
        mock_transfer.side_effect = lambda *args, **kwargs: (
            calls.append(f"upload {args[2]}") or 10
        )

        copied = self._copy(
            [
                {"id": "sv-1", "name": "v1"},
                {"id": "sv-2", "name": "v2"},
            ]
        )

        self.assertEqual(copied, ["v1", "v2"])
        self.assertEqual(
            calls, ["create v1", "upload a.csv", "create v2", "upload b.csv"]
        )
        self.assertEqual(self.ds_result.files_copied, 2)
        self.assertEqual(self.ds_result.bytes_copied, 20)

    @patch("hexa.workspace_copier.resources.datasets._transfer_file")
    @patch("hexa.workspace_copier.resources.datasets._prepare_download")
    @patch("hexa.workspace_copier.resources.datasets._list_version_files")
    @patch("hexa.workspace_copier.resources.datasets._create_version")
    def test_a_failed_file_stops_before_the_next_version_is_created(
        self, mock_create, mock_files, mock_download, mock_transfer
    ):
        # Creating v2 would lock the incomplete v1 out of any further upload, so
        # the whole dataset is abandoned instead.
        mock_create.return_value = "tv-1"
        mock_files.return_value = [
            {"id": "f1", "uri": "sd-1/sv-1/a.csv", "filename": "a.csv"}
        ]
        mock_download.return_value = "https://download"
        mock_transfer.side_effect = GraphQLError("upload returned HTTP 500")

        with self.assertRaises(GraphQLError) as ctx:
            self._copy([{"id": "sv-1", "name": "v1"}, {"id": "sv-2", "name": "v2"}])

        self.assertIn("a.csv", str(ctx.exception))
        self.assertIn("later versions were not copied", str(ctx.exception))
        self.assertEqual(mock_create.call_count, 1)

    @patch("hexa.workspace_copier.resources.datasets._transfer_file")
    @patch("hexa.workspace_copier.resources.datasets._prepare_download")
    @patch("hexa.workspace_copier.resources.datasets._list_version_files")
    @patch("hexa.workspace_copier.resources.datasets._create_version")
    def test_a_file_with_no_content_on_source_is_warned_and_skipped(
        self, mock_create, mock_files, mock_download, mock_transfer
    ):
        mock_create.return_value = "tv-1"
        mock_files.return_value = [
            {"id": "f1", "uri": "sd-1/sv-1/a.csv", "filename": "a.csv"}
        ]
        mock_download.return_value = None  # FILE_NOT_UPLOADED on the source

        copied = self._copy([{"id": "sv-1", "name": "v1"}])

        self.assertEqual(copied, ["v1"])
        mock_transfer.assert_not_called()
        self.assertEqual(self.ds_result.files_copied, 0)
        self.assertTrue(any("a.csv" in w for w in self.ds_result.warnings))


class DatasetsCopierOptionsTest(SimpleTestCase):
    @patch("hexa.workspace_copier.resources.datasets._copy_versions")
    @patch("hexa.workspace_copier.resources.datasets._apply_sharing")
    @patch("hexa.workspace_copier.resources.datasets._create_on_target")
    @patch("hexa.workspace_copier.resources.datasets._select_versions")
    @patch("hexa.workspace_copier.resources.datasets._fetch_source_detail")
    @patch("hexa.workspace_copier.resources.datasets._list_target_slugs")
    @patch("hexa.workspace_copier.resources.datasets._list_source_datasets")
    def test_all_dataset_versions_flag_reaches_the_version_selection(
        self,
        mock_list,
        mock_target_slugs,
        mock_detail,
        mock_select,
        mock_create,
        mock_sharing,
        mock_versions,
    ):
        mock_list.return_value = [("sd-1", "my-dataset", "My Dataset")]
        mock_target_slugs.return_value = set()
        mock_detail.return_value = _detail()
        mock_create.return_value = ("td-1", "my-dataset")
        mock_select.return_value = []
        mock_versions.return_value = []

        DatasetsCopier().copy(
            Endpoint.remote(MagicMock(), "src"),
            Endpoint.remote(MagicMock(), "tgt"),
            CopyResult(),
            NullReporter(),
            options=CopyOptions(all_dataset_versions=True),
        )

        self.assertIs(mock_select.call_args.args[3], True)
