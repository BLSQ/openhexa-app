import json
import os
from unittest import mock

import pandas as pd
from pandas.errors import ParserError

from hexa.core.test import TestCase
from hexa.datasets.models import DatasetFileMetadata
from hexa.datasets.queue import generate_dataset_file_sample_task
from hexa.files.api import get_storage


class TestCreateDatasetFileMetadataTask(TestCase):
    @mock.patch("hexa.datasets.queue.DatasetVersionFile.objects.get")
    @mock.patch("hexa.datasets.queue.DatasetFileMetadata.objects.create")
    @mock.patch("hexa.datasets.queue.generate_download_url")
    def test_create_dataset_file_metadata_task_success(
        self,
        mock_generate_download_url,
        mock_DatasetFileMetadata_create,
        mock_DatasetVersionFile_get,
    ):
        test_cases = [
            (
                "example_names.csv",
                DatasetFileMetadata.STATUS_FINISHED,
                '[{"name":"Jack","surname":"Howard"},{"name":"Olivia","surname":"Brown"},{"name":"Lily","surname":"Evan',
            ),
            (
                "example_names_2_lines.csv",
                DatasetFileMetadata.STATUS_FINISHED,
                '[{"name":"Liam","surname":"Smith"},{"name":"Joe","surname":"Doe"},{"name":"Joe","surname":"Doe"},{"nam',
            ),
            (
                "example_names_0_lines.csv",
                DatasetFileMetadata.STATUS_FINISHED,
                "[]",
            ),
            (
                "example_names.parquet",
                DatasetFileMetadata.STATUS_FINISHED,
                '[{"name":"Jack","surname":"Howard"},{"name":"Olivia","surname":"Brown"},{"name":"Lily","surname":"Evan',
            ),
            (
                "example_names.xlsx",
                DatasetFileMetadata.STATUS_FINISHED,
                '[{"name":"Jack","surname":"Howard"},{"name":"Olivia","surname":"Brown"},{"name":"Lily","surname":"Evan',
            ),
        ]
        for filename, expected_status, expected_content in test_cases:
            with self.subTest(filename=filename):
                dataset_version_file = mock.Mock()
                dataset_version_file.id = 1
                dataset_version_file.filename = f"{filename}"
                mock_DatasetVersionFile_get.return_value = dataset_version_file

                dataset_file_metadata = mock.Mock()
                mock_DatasetFileMetadata_create.return_value = dataset_file_metadata

                fixture_file_path = os.path.join(
                    os.path.dirname(__file__), f"./fixtures/{filename}"
                )
                mock_generate_download_url.return_value = fixture_file_path

                job = mock.Mock()
                job.args = {"file_id": dataset_version_file.id}

                generate_dataset_file_sample_task(mock.Mock(), job)

                mock_generate_download_url.assert_called_once_with(dataset_version_file)
                mock_DatasetVersionFile_get.assert_called_once_with(
                    id=dataset_version_file.id
                )
                mock_DatasetFileMetadata_create.assert_called_once_with(
                    dataset_version_file=dataset_version_file,
                    status=DatasetFileMetadata.STATUS_PROCESSING,
                )
                dataset_file_metadata.save.assert_called()
                self.assertEqual(dataset_file_metadata.status, expected_status)
                self.assertEqual(
                    dataset_file_metadata.sample[0 : len(expected_content)],
                    expected_content,
                )

                mock_generate_download_url.reset_mock()
                mock_DatasetVersionFile_get.reset_mock()
                mock_DatasetFileMetadata_create.reset_mock()
                dataset_file_metadata.save.reset_mock()

    @mock.patch("hexa.datasets.queue.DatasetVersionFile.objects.get")
    @mock.patch("hexa.datasets.queue.DatasetFileMetadata.objects.create")
    @mock.patch("hexa.datasets.queue.generate_download_url")
    def test_create_dataset_file_metadata_task_failure(
        self,
        mock_generate_download_url,
        mock_DatasetFileMetadata_create,
        mock_DatasetVersionFile_get,
    ):
        test_cases = [
            (get_storage().exceptions.NotFound, DatasetFileMetadata.STATUS_FAILED),
            (ValueError, DatasetFileMetadata.STATUS_FAILED),
            (ParserError, DatasetFileMetadata.STATUS_FAILED),
        ]
        for exception, expected_status in test_cases:
            with self.subTest(exception=exception):
                dataset_version_file = mock.Mock()
                dataset_version_file.id = 1
                dataset_version_file.filename = "example_names.csv"
                mock_DatasetVersionFile_get.return_value = dataset_version_file

                dataset_file_metadata = mock.Mock()
                mock_DatasetFileMetadata_create.return_value = dataset_file_metadata

                mock_generate_download_url.side_effect = exception

                job = mock.Mock()
                job.args = {"file_id": dataset_version_file.id}
                generate_dataset_file_sample_task(mock.Mock(), job)

                mock_DatasetVersionFile_get.assert_called_with(
                    id=dataset_version_file.id
                )
                dataset_file_metadata.save.assert_called()
                self.assertEqual(dataset_file_metadata.status, expected_status)

                mock_generate_download_url.reset_mock()
                mock_DatasetVersionFile_get.reset_mock()
                mock_DatasetFileMetadata_create.reset_mock()
                dataset_file_metadata.save.reset_mock()

    @mock.patch("hexa.datasets.queue.DatasetVersionFile.objects.get")
    @mock.patch("hexa.datasets.queue.DatasetFileMetadata.objects.create")
    @mock.patch("hexa.datasets.queue.generate_download_url")
    def test_create_dataset_file_metadata_task_failure_empty_file(
        self,
        mock_generate_download_url,
        mock_DatasetFileMetadata_create,
        mock_DatasetVersionFile_get,
    ):
        dataset_version_file = mock.Mock()
        dataset_version_file.id = 1
        dataset_version_file.filename = "example_empty_file.csv"
        mock_DatasetVersionFile_get.return_value = dataset_version_file

        dataset_file_metadata = mock.Mock()
        mock_DatasetFileMetadata_create.return_value = dataset_file_metadata

        fixture_file_path = os.path.join(
            os.path.dirname(__file__), "./fixtures/example_empty_file.csv"
        )
        mock_generate_download_url.return_value = fixture_file_path

        job = mock.Mock()
        job.args = {"file_id": dataset_version_file.id}

        generate_dataset_file_sample_task(mock.Mock(), job)

        mock_generate_download_url.assert_called_once_with(dataset_version_file)
        mock_DatasetVersionFile_get.assert_called_once_with(id=dataset_version_file.id)
        mock_DatasetFileMetadata_create.assert_called_once_with(
            dataset_version_file=dataset_version_file,
            status=DatasetFileMetadata.STATUS_PROCESSING,
        )
        dataset_file_metadata.save.assert_called()
        self.assertEqual(
            dataset_file_metadata.status, DatasetFileMetadata.STATUS_FAILED
        )
        self.assertEqual(
            dataset_file_metadata.status_reason, "No columns to parse from file"
        )


class TestFileFillMetadata(TestCase):
    @mock.patch("hexa.datasets.queue.DatasetVersionFile.objects.get")
    @mock.patch("hexa.datasets.queue.DatasetFileMetadata.objects.create")
    @mock.patch("hexa.datasets.queue.generate_download_url")
    def test_fill_in_metadata(
        self,
        mock_generate_download_url,
        mock_DatasetFileMetadata_create,
        mock_DatasetVersionFile_get,
    ):
        filename = "example_names.csv"
        dataset_version_file = mock.Mock()
        dataset_version_file.id = 1
        dataset_version_file.filename = f"{filename}"
        mock_DatasetVersionFile_get.return_value = dataset_version_file

        dataset_file_metadata = mock.Mock()
        mock_DatasetFileMetadata_create.return_value = dataset_file_metadata

        fixture_file_path = os.path.join(
            os.path.dirname(__file__), f"./fixtures/{filename}"
        )
        mock_generate_download_url.return_value = fixture_file_path

        job = mock.Mock()
        job.args = {"file_id": dataset_version_file.id}

        generate_dataset_file_sample_task(mock.Mock(), job)
        print(
            f"status: {dataset_file_metadata.status} : reason: {dataset_file_metadata.status_reason}"
        )
        data = json.loads(dataset_file_metadata.profiling)
        decoded_profiling = {key: json.loads(value) for key, value in data.items()}
        data_pd = pd.DataFrame(decoded_profiling)
        dtype_spec = {
            "column_names": "string",
            "data_types": "string",
            "missing_values": "int",
            "unique_values": "int",
            "distinct_values": "int",
            "constant_values": "string",
        }
        data_pd.to_csv(fixture_file_path.replace(".csv", "_result.csv"), index=False)
        expected_profiling = pd.read_csv(
            fixture_file_path.replace(".csv", "_result.csv"), dtype=dtype_spec
        )

        data_pd, expected_data_pd = data_pd.align(
            expected_profiling, join="outer", axis=1
        )
        data_pd = data_pd.sort_index(axis=1)
        expected_data_pd = expected_data_pd.sort_index(axis=1)

        self.assertEqual(data_pd.equals(expected_data_pd), True)
