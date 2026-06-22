from unittest.mock import MagicMock, patch

import httpx
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.progress import NullReporter
from hexa.workspace_duplicator.service import (
    CredentialError,
    _verify_endpoints,
    _verify_side,
    run_migration,
)
from hexa.workspace_duplicator.transport import GraphQLError


def _kwargs(**overrides):
    """Both sides remote by default, so verification never touches the DB."""
    data = {
        "source_url": "http://src/graphql/",
        "source_email": "admin@example.org",
        "source_password": "secret",
        "source_slug": "my-ws",
        "target_url": "http://tgt/graphql/",
        "target_email": "admin@example.org",
        "target_password": "secret",
        "target_organization_id": "org-1",
        "target_workspace_name": None,
    }
    data.update(overrides)
    return data


class VerifySideTest(SimpleTestCase):
    def test_success_returns_endpoint_and_no_error(self):
        endpoint = Endpoint.local("src")
        result, error = _verify_side("source", lambda: endpoint)
        self.assertIs(result, endpoint)
        self.assertIsNone(error)

    def test_graphql_error_passes_message_through(self):
        def build():
            raise GraphQLError("source login failed: invalid credentials")

        result, error = _verify_side("source", build)
        self.assertIsNone(result)
        self.assertEqual(error, "source login failed: invalid credentials")

    def test_connection_error_maps_to_unreachable(self):
        def build():
            raise httpx.ConnectError("connection refused")

        result, error = _verify_side("target", build)
        self.assertIsNone(result)
        self.assertEqual(error, "target server is unreachable (ConnectError).")

    def test_missing_local_workspace_maps_to_labeled_error(self):
        def build():
            raise ObjectDoesNotExist("Workspace matching query does not exist.")

        result, error = _verify_side("source", build)
        self.assertIsNone(result)
        self.assertEqual(error, "source: Workspace matching query does not exist.")


class CredentialErrorTest(SimpleTestCase):
    def test_is_a_graphql_error_and_carries_per_side_messages(self):
        err = CredentialError(["first", "second"])
        self.assertIsInstance(err, GraphQLError)
        self.assertEqual(err.errors, ["first", "second"])
        self.assertEqual(str(err), "first; second")


class VerifyEndpointsTest(SimpleTestCase):
    @patch("hexa.workspace_duplicator.service.build_client")
    def test_both_sides_failing_reports_both_messages(self, mock_build):
        mock_build.side_effect = [
            GraphQLError("source login failed: bad"),
            GraphQLError("target login failed: bad"),
        ]
        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs())
        self.assertEqual(
            ctx.exception.errors,
            ["source login failed: bad", "target login failed: bad"],
        )

    @patch("hexa.workspace_duplicator.service.build_client")
    def test_single_side_failure_reports_one_message(self, mock_build):
        mock_build.side_effect = [GraphQLError("source login failed: bad"), MagicMock()]
        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs())
        self.assertEqual(ctx.exception.errors, ["source login failed: bad"])

    @patch("hexa.workspace_duplicator.service.build_client")
    def test_unreachable_hosts_are_reported(self, mock_build):
        mock_build.side_effect = [
            httpx.ConnectError("x"),
            httpx.ConnectError("x"),
        ]
        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs())
        self.assertEqual(
            ctx.exception.errors,
            [
                "source server is unreachable (ConnectError).",
                "target server is unreachable (ConnectError).",
            ],
        )

    @patch("hexa.workspace_duplicator.service.build_client")
    def test_success_returns_both_endpoints(self, mock_build):
        src_client, tgt_client = MagicMock(), MagicMock()
        mock_build.side_effect = [src_client, tgt_client]

        source, target = _verify_endpoints(**_kwargs())

        self.assertTrue(source.is_remote)
        self.assertIs(source.client, src_client)
        self.assertEqual(source.slug, "my-ws")
        self.assertTrue(target.is_remote)
        self.assertIs(target.client, tgt_client)
        self.assertEqual(target.organization_id, "org-1")


class RunMigrationTest(SimpleTestCase):
    @patch("hexa.workspace_duplicator.service.duplicate_workspace")
    @patch("hexa.workspace_duplicator.service.build_client")
    def test_proceeds_to_copy_after_successful_verification(self, mock_build, mock_dup):
        mock_build.side_effect = [MagicMock(), MagicMock()]
        sentinel = object()
        mock_dup.return_value = sentinel

        result = run_migration(
            resources={"workspace"}, reporter=NullReporter(), **_kwargs()
        )

        self.assertIs(result, sentinel)
        mock_dup.assert_called_once()

    @patch("hexa.workspace_duplicator.service.duplicate_workspace")
    @patch("hexa.workspace_duplicator.service.build_client")
    def test_aborts_before_copy_on_bad_credentials(self, mock_build, mock_dup):
        mock_build.side_effect = GraphQLError("source login failed: bad")

        with self.assertRaises(CredentialError):
            run_migration(reporter=NullReporter(), **_kwargs())

        mock_dup.assert_not_called()
