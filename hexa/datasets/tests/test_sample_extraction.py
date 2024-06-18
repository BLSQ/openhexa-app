import json
import os
from unittest import mock

import pandas as pd

from hexa.core.test import TestCase
from hexa.datasets.queue import (
    calculate_profiling_per_column,
    dataframe_to_sample,
    download_file_as_dataframe,
    is_supported_mimetype,
)


class TestCreateDatasetFileSample(TestCase):
    @mock.patch("hexa.datasets.queue.generate_download_url")
    def test_generate_file_metadata_task_success(
        self,
        mock_generate_download_url,
    ):
        test_cases = [
            (
                "example_names.csv",
                '[{"name":"Jack","surname":"Howard"},{"name":"Olivia","surname":"Brown"}]',
            ),
            (
                "example_names_2_lines.csv",
                '[{"name":"Liam","surname":"Smith"},{"name":"Joe","surname":"Doe"}]',
            ),
            (
                "example_names.parquet",
                '[{"name":"Jack","surname":"Howard"},{"name":"Olivia","surname":"Brown"}]',
            ),
            (
                "example_names.xlsx",
                '[{"name":"Jack","surname":"Howard"},{"name":"Olivia","surname":"Brown"}]',
            ),
        ]
        for filename, expected_content in test_cases:
            with self.subTest(filename=filename):
                # Mock out the dependencies used in generate_file_metadata_task method we try to test
                mock_dataset_version_file = mock.Mock(id=1, filename=filename)

                # Path to mocked fixture to test
                fixture_file_path = os.path.join(
                    os.path.dirname(__file__), f"./fixtures/{filename}"
                )
                mock_generate_download_url.return_value = fixture_file_path

                # Test sample generation
                self.assertTrue(is_supported_mimetype(filename))
                dataframe = download_file_as_dataframe(
                    dataset_version_file=mock_dataset_version_file
                )
                self.assertIsNotNone(dataframe)
                sample_slice = (
                    dataframe_to_sample(dataframe).iloc[:2, :].reset_index(drop=True)
                )

                # Assert result with expected fixture
                expected = pd.DataFrame(json.loads(expected_content))
                self.assertTrue(sample_slice.equals(expected))

                # reset mocks for each case run
                mock_generate_download_url.assert_called_once_with(
                    mock_dataset_version_file
                )
                mock_generate_download_url.reset_mock()

    @mock.patch("hexa.datasets.queue.generate_download_url")
    def test_automated_profiling_generation(
        self,
        mock_generate_download_url,
    ):
        filenames = ["example_names_with_age.csv", "senegal_rural_raw.csv"]
        for filename in filenames:
            # Mock out the dependencies used in generate_file_metadata_task method we try to test
            mock_dataset_version_file = mock.Mock(id=1, filename=filename)

            # Path to mocked fixture to test
            fixture_file_path = os.path.join(
                os.path.dirname(__file__), f"./fixtures/{filename}"
            )
            mock_generate_download_url.return_value = fixture_file_path

            # Test sample generation
            self.assertTrue(is_supported_mimetype(filename))
            dataframe = download_file_as_dataframe(
                dataset_version_file=mock_dataset_version_file
            )
            profiling = calculate_profiling_per_column(dataframe)

            # Assert result with expected fixture
            expected_profiling = pd.read_csv(
                fixture_file_path.replace(".csv", "_profiling.csv")
            ).sort_index(axis=1)
            comparison = expected_profiling.compare(
                pd.DataFrame(profiling).sort_index(axis=1)
            )
            self.assertTrue(comparison.empty)

            # reset mocks for each case run
            mock_generate_download_url.assert_called_once_with(
                mock_dataset_version_file
            )
            mock_generate_download_url.reset_mock()
