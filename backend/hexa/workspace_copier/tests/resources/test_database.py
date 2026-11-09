from unittest.mock import MagicMock, patch

import psycopg2

from hexa.core.test import TestCase
from hexa.databases.api import DatabaseInUse, DatabaseNotEmpty
from hexa.user_management.models import User
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.database import (
    NOT_ON_THIS_SERVER,
    DatabaseCopier,
)
from hexa.workspace_copier.results import CopyResult, format_summary
from hexa.workspaces.tests.testutils import create_workspace

MODULE = "hexa.workspace_copier.resources.database"


@patch(f"{MODULE}.replace_empty_database_with_copy")
class DatabaseCopierTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user = User.objects.create_user(
            "copier@bluesquarehub.com", "password", is_superuser=True
        )
        cls.SOURCE = create_workspace(user, name="Source")
        cls.TARGET = create_workspace(user, name="Target")

    def _copy(self, source_slug=None, target_slug=None, *, same_server=True):
        result = CopyResult()
        DatabaseCopier().copy(
            Endpoint(MagicMock(), source_slug or self.SOURCE.slug),
            Endpoint(MagicMock(), target_slug or self.TARGET.slug),
            result,
            NullReporter(),
            options=CopyOptions(same_server=same_server),
        )
        return result

    def test_same_server_copy_copies(self, replace):
        result = self._copy()

        replace.assert_called_once_with(self.SOURCE.db_name, self.TARGET.db_name)
        self.assertTrue(result.database.copied)
        self.assertIn("Database: copied", format_summary(result))

    def test_without_same_server_is_skipped_with_instructions(self, replace):
        result = self._copy(same_server=False)

        replace.assert_not_called()
        instructions = result.database.skipped
        self.assertIn(
            "only copied when both workspaces are on this server", instructions
        )
        self.assertIn(f"/workspaces/{self.SOURCE.slug}/databases", instructions)
        self.assertIn(f"/workspaces/{self.TARGET.slug}/databases", instructions)
        self.assertIn(
            "./manage.py copy_workspace --same-server --source-workspace-slug "
            f"{self.SOURCE.slug} --target-workspace-slug {self.TARGET.slug} "
            "--resources database",
            instructions,
        )
        self.assertIn('pg_dump -Fc --no-owner --no-acl "$SOURCE_URL"', instructions)

    def test_workspace_missing_from_this_server_is_reported_as_failed(self, replace):
        result = self._copy(target_slug="on-another-server")

        replace.assert_not_called()
        self.assertEqual(result.database.failed, NOT_ON_THIS_SERVER)

    def test_target_with_data_is_skipped(self, replace):
        replace.side_effect = DatabaseNotEmpty(self.TARGET.db_name)

        result = self._copy()

        self.assertFalse(result.database.copied)
        self.assertIsNone(result.database.failed)
        self.assertIn("already contains data", result.database.skipped)

    def test_source_in_use_is_reported_as_failed(self, replace):
        replace.side_effect = DatabaseInUse(self.SOURCE.db_name, 2)

        result = self._copy()

        self.assertFalse(result.database.copied)
        self.assertIn("has 2 open connection(s)", result.database.failed)
        self.assertIn("could NOT be copied", format_summary(result))

    def test_database_error_is_reported_as_failed(self, replace):
        replace.side_effect = psycopg2.OperationalError("server closed the connection")

        result = self._copy()

        self.assertEqual(result.database.failed, "server closed the connection")
