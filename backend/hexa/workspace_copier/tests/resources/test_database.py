from unittest.mock import MagicMock

from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.database import DatabaseCopier
from hexa.workspace_copier.results import CopyResult


class DatabaseCopierTest(SimpleTestCase):
    def test_remote_source_records_warning_and_returns(self):
        source = Endpoint.remote(MagicMock(), "src")
        target = Endpoint.local("tgt")
        result = CopyResult()

        DatabaseCopier().copy(source, target, result, NullReporter())

        self.assertTrue(
            any("both endpoints must be local" in w for w in result.warnings)
        )

    def test_remote_target_records_warning_and_returns(self):
        source = Endpoint.local("src")
        target = Endpoint.remote(MagicMock(), "tgt")
        result = CopyResult()

        DatabaseCopier().copy(source, target, result, NullReporter())

        self.assertTrue(
            any("both endpoints must be local" in w for w in result.warnings)
        )

    def test_local_to_local_not_yet_implemented(self):
        source = Endpoint.local("src")
        target = Endpoint.local("tgt")
        result = CopyResult()

        with self.assertRaises(NotImplementedError):
            DatabaseCopier().copy(source, target, result, NullReporter())
