from unittest.mock import MagicMock

from django.utils.crypto import get_random_string

from hexa.core.test import TestCase
from hexa.pipelines.utils import generate_pipeline_container_name


class PipelineUtilsTest(TestCase):
    def test_generate_pipeline_container_name(self):
        run = MagicMock()
        run.code = get_random_string(50)

        container_name = generate_pipeline_container_name(run)
        self.assertTrue(len(container_name) <= 63)

        run.code = get_random_string(100)

        container_name = generate_pipeline_container_name(run)
        self.assertTrue(len(container_name) <= 63)
