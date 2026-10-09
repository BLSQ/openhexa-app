from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from openhexa.graphql.graphql_client.exceptions import GraphQLClientError

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.connections import ConnectionsCopier
from hexa.workspace_copier.results import CopyResult


def _conn(slug, fields):
    return {
        "id": "1",
        "name": slug.upper(),
        "slug": slug,
        "description": "",
        "type": "POSTGRESQL",
        "fields": fields,
    }


class ConnectionsCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = CopyResult()

    @patch("hexa.workspace_copier.resources.connections._list_connections")
    def test_creates_missing_connection(self, mock_list):
        mock_list.side_effect = [
            [_conn("db", [{"code": "host", "value": "h", "secret": False}])],
            [],  # target has none
        ]
        self.target.client.create_connection.return_value = MagicMock(
            success=True, connection=MagicMock()
        )

        ConnectionsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.connections.created, [("db", 1)])
        self.assertEqual(self.result.connections.skipped, [])

    @patch("hexa.workspace_copier.resources.connections._list_connections")
    def test_skips_existing_connection(self, mock_list):
        mock_list.side_effect = [
            [_conn("db", [])],
            [{"slug": "db"}],  # already on target
        ]

        ConnectionsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.connections.skipped, ["db"])
        self.target.client.create_connection.assert_not_called()

    @patch("hexa.workspace_copier.resources.connections._list_connections")
    def test_empty_secret_is_flagged(self, mock_list):
        mock_list.side_effect = [
            [_conn("db", [{"code": "password", "value": None, "secret": True}])],
            [],
        ]
        self.target.client.create_connection.return_value = MagicMock(
            success=True, connection=MagicMock()
        )

        ConnectionsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertTrue(any("secret" in w for w in self.result.connections.warnings))
        fields = self.target.client.create_connection.call_args.kwargs["input"].fields
        self.assertEqual(fields[0].value, "")

    @patch("hexa.workspace_copier.resources.connections._list_connections")
    def test_sdk_error_is_recorded_as_failure(self, mock_list):
        mock_list.side_effect = [[_conn("db", []), _conn("api", [])], []]
        self.target.client.create_connection.side_effect = [
            GraphQLClientError("boom"),
            MagicMock(success=True, connection=MagicMock()),
        ]

        ConnectionsCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.connections.failed, ["db"])
        self.assertEqual(self.result.connections.created, [("api", 0)])

    def _copy_db_with_password(self, mock_list, options):
        mock_list.side_effect = [
            [
                _conn(
                    "db",
                    [
                        {"code": "host", "value": "h", "secret": False},
                        {"code": "password", "value": "pw", "secret": True},
                    ],
                )
            ],
            [],
        ]
        self.target.client.create_connection.return_value = MagicMock(
            success=True, connection=MagicMock()
        )
        ConnectionsCopier().copy(
            self.source, self.target, self.result, NullReporter(), options=options
        )
        fields = self.target.client.create_connection.call_args.kwargs["input"].fields
        return {f.code: f.value for f in fields}

    @patch("hexa.workspace_copier.resources.connections._list_connections")
    def test_secrets_copied_by_default(self, mock_list):
        values = self._copy_db_with_password(mock_list, CopyOptions())

        self.assertEqual(values, {"host": "h", "password": "pw"})
        self.assertEqual(self.result.connections.warnings, [])

    @patch("hexa.workspace_copier.resources.connections._list_connections")
    def test_secrets_blanked_when_excluded(self, mock_list):
        values = self._copy_db_with_password(
            mock_list, CopyOptions(include_connection_secrets=False)
        )

        self.assertEqual(values, {"host": "h", "password": ""})
        self.assertEqual(len(self.result.connections.warnings), 1)

    def test_local_endpoint_not_yet_implemented(self):
        with self.assertRaises(NotImplementedError):
            ConnectionsCopier().copy(
                Endpoint.local("src"), self.target, self.result, NullReporter()
            )
