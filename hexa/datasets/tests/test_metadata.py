import os
from unittest import mock

from hexa.core.test import TestCase
from hexa.datasets.models import DatasetFileMetadata
from hexa.datasets.queue import generate_dataset_file_metadata_task
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
            ("example_names.csv", DatasetFileMetadata.STATUS_FINISHED),
            ("example_names.parquet", DatasetFileMetadata.STATUS_FINISHED),
        ]
        for filename, expected_status in test_cases:
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

                generate_dataset_file_metadata_task(mock.Mock(), job)

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
                expected_content = '[{"name":"Sofia","surname":"Walker"},{"name":"Aiden","surname":"Adams"},{"name":"Eleanor","surname":"H'
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
        dataset_version_file = mock.Mock()
        dataset_version_file.id = 1
        dataset_version_file.filename = "example_names.csv"
        mock_DatasetVersionFile_get.return_value = dataset_version_file

        dataset_file_metadata = mock.Mock()
        mock_DatasetFileMetadata_create.return_value = dataset_file_metadata

        mock_generate_download_url.side_effect = get_storage().exceptions.NotFound

        job = mock.Mock()
        job.args = {"file_id": dataset_version_file.id}
        generate_dataset_file_metadata_task(mock.Mock(), job)

        mock_DatasetVersionFile_get.assert_called_with(id=dataset_version_file.id)
        dataset_file_metadata.save.assert_called()
        self.assertEqual(
            dataset_file_metadata.status, DatasetFileMetadata.STATUS_FAILED
        )
