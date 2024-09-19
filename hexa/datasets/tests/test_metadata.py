import os
from unittest.mock import patch

from django.test import override_settings

from hexa.core.test import TestCase
from hexa.datasets.models import Dataset, DatasetFileMetadata, DatasetVersionFile
from hexa.datasets.queue import generate_sample
from hexa.files import storage
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class TestCreateDatasetFileMetadataTask(TestCase):
    @classmethod
    def setUpTestData(cls):
        storage.reset()
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com", "serena's password", is_superuser=True
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SERENA, name="My Workspace", description="Test workspace"
        )

        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_SERENA,
            cls.WORKSPACE,
            name="Dataset",
            description="Dataset's description",
        )
        cls.DATASET_VERSION = cls.DATASET.create_version(
            principal=cls.USER_SERENA, name="v1"
        )

    @override_settings(WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE=3)
    def test_generate_sample(
        self,
    ):
        CASES = [
            # It fails because the file is empty (no columns to parse)
            (
                "example_empty_file.csv",
                DatasetFileMetadata.STATUS_FAILED,
                [],
                "No columns to parse from file",
            ),
            (
                "example_names.csv",
                DatasetFileMetadata.STATUS_FINISHED,
                [
                    {"name": "Jack", "surname": "Howard"},
                    {"name": "Olivia", "surname": "Brown"},
                    {"name": "Lily", "surname": "Evans"},
                ],
                None,
            ),
            # The CSV only contains 2 lines so it's going to add existing lines to achieve the desired sample size
            (
                "example_names_2_lines.csv",
                DatasetFileMetadata.STATUS_FINISHED,
                [
                    {"name": "Liam", "surname": "Smith"},
                    {"name": "Joe", "surname": "Doe"},
                    {"name": "Joe", "surname": "Doe"},
                ],
                None,
            ),
            (
                "example_names_0_lines.csv",
                DatasetFileMetadata.STATUS_FINISHED,
                [],
                None,
            ),
            (
                "example_names.parquet",
                DatasetFileMetadata.STATUS_FINISHED,
                [
                    {"name": "Jack", "surname": "Howard"},
                    {"name": "Olivia", "surname": "Brown"},
                    {"name": "Lily", "surname": "Evans"},
                ],
                None,
            ),
            (
                "example_names.xlsx",
                DatasetFileMetadata.STATUS_FINISHED,
                [
                    {"name": "Jack", "surname": "Howard"},
                    {"name": "Olivia", "surname": "Brown"},
                    {"name": "Lily", "surname": "Evans"},
                ],
                None,
            ),
        ]
        for (
            fixture_name,
            expected_status,
            expected_sample,
            expected_status_reason,
        ) in CASES:
            with self.subTest(fixture_name=fixture_name):
                fixture_file_path = os.path.join(
                    os.path.dirname(__file__), f"./fixtures/{fixture_name}"
                )
                version_file = DatasetVersionFile.objects.create_if_has_perm(
                    self.USER_SERENA,
                    self.DATASET_VERSION,
                    uri=fixture_file_path,
                    content_type="application/octect-stream",
                )

                with patch(
                    "hexa.datasets.queue.generate_download_url"
                ) as mock_generate_download_url:
                    mock_generate_download_url.return_value = fixture_file_path
                    sample_entry = generate_sample(version_file)
                    self.assertEqual(sample_entry.status, expected_status)
                    self.assertEqual(sample_entry.sample, expected_sample)

                    if expected_status_reason:
                        self.assertEqual(
                            sample_entry.status_reason, expected_status_reason
                        )
