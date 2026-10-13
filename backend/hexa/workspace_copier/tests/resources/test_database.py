from unittest.mock import MagicMock, patch

import psycopg2

from hexa.core.test import TestCase
from hexa.databases.api import DatabaseInUse, DatabaseNotEmpty
from hexa.user_management.models import User
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.database import DatabaseCopier
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

    def _copy(self, source, target):
        result = CopyResult()
        DatabaseCopier().copy(source, target, result, NullReporter())
        return result

    def test_local_to_local_copies(self, replace):
        result = self._copy(
            Endpoint.local(self.SOURCE.slug), Endpoint.local(self.TARGET.slug)
        )

        replace.assert_called_once_with(self.SOURCE.db_name, self.TARGET.db_name)
        self.assertTrue(result.database.copied)
        self.assertIn("Database: copied", format_summary(result))

    def test_remote_source_is_skipped_with_instructions(self, replace):
        result = self._copy(
            Endpoint.remote(MagicMock(), "remote-source"),
            Endpoint.local(self.TARGET.slug),
        )

        replace.assert_not_called()
        instructions = result.database.skipped
        self.assertIn(
            "only copied when both source and target are this server", instructions
        )
        self.assertIn("/workspaces/remote-source/databases", instructions)
        self.assertIn(f"/workspaces/{self.TARGET.slug}/databases", instructions)
        self.assertIn(
            "./manage.py copy_workspace --source-workspace-slug remote-source "
            f"--target-workspace-slug {self.TARGET.slug} --resources database",
            instructions,
        )
        self.assertIn('pg_dump -Fc --no-owner --no-acl "$SOURCE_URL"', instructions)

    def test_remote_target_is_skipped(self, replace):
        result = self._copy(
            Endpoint.local(self.SOURCE.slug),
            Endpoint.remote(MagicMock(), "remote-target"),
        )

        replace.assert_not_called()
        self.assertIn("only copied when both", result.database.skipped)

    def test_target_with_data_is_skipped(self, replace):
        replace.side_effect = DatabaseNotEmpty(self.TARGET.db_name)

        result = self._copy(
            Endpoint.local(self.SOURCE.slug), Endpoint.local(self.TARGET.slug)
        )

        self.assertFalse(result.database.copied)
        self.assertIsNone(result.database.failed)
        self.assertIn("already contains data", result.database.skipped)

    def test_source_in_use_is_reported_as_failed(self, replace):
        replace.side_effect = DatabaseInUse(self.SOURCE.db_name, 2)

        result = self._copy(
            Endpoint.local(self.SOURCE.slug), Endpoint.local(self.TARGET.slug)
        )

        self.assertFalse(result.database.copied)
        self.assertIn("has 2 open connection(s)", result.database.failed)
        self.assertIn("could NOT be copied", format_summary(result))

    def test_database_error_is_reported_as_failed(self, replace):
        replace.side_effect = psycopg2.OperationalError("server closed the connection")

        result = self._copy(
            Endpoint.local(self.SOURCE.slug), Endpoint.local(self.TARGET.slug)
        )

        self.assertEqual(result.database.failed, "server closed the connection")
