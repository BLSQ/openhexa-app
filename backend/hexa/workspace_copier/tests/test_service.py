from unittest.mock import MagicMock, patch

import httpx
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.service import (
    CredentialError,
    _verify_endpoints,
    _verify_side,
    run_copy,
    run_template_copy,
)
from hexa.workspace_copier.transport import GraphQLError


def _kwargs(**overrides):
    """Both sides remote by default, so verification never touches the DB."""
    data = {
        "source_url": "http://src/graphql/",
        "source_token": "src-token",
        "source_slug": "my-ws",
        "target_url": "http://tgt/graphql/",
        "target_token": "tgt-token",
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
            raise GraphQLError("source authentication failed: invalid credentials")

        result, error = _verify_side("source", build)
        self.assertIsNone(result)
        self.assertEqual(error, "source authentication failed: invalid credentials")

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
    @patch("hexa.workspace_copier.service.build_client")
    def test_both_sides_failing_reports_both_messages(self, mock_build):
        mock_build.side_effect = [
            GraphQLError("source authentication failed: bad"),
            GraphQLError("target authentication failed: bad"),
        ]
        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs())
        self.assertEqual(
            ctx.exception.errors,
            ["source authentication failed: bad", "target authentication failed: bad"],
        )

    @patch("hexa.workspace_copier.service.build_client")
    def test_single_side_failure_reports_one_message(self, mock_build):
        mock_build.side_effect = [
            GraphQLError("source authentication failed: bad"),
            MagicMock(),
        ]
        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs())
        self.assertEqual(ctx.exception.errors, ["source authentication failed: bad"])

    @patch("hexa.workspace_copier.service.build_client")
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

    @patch("hexa.workspace_copier.service.build_client")
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


class RunCopyTest(SimpleTestCase):
    @patch("hexa.workspace_copier.service.copy_workspace")
    @patch("hexa.workspace_copier.service.build_client")
    def test_proceeds_to_copy_after_successful_verification(self, mock_build, mock_dup):
        mock_build.side_effect = [MagicMock(), MagicMock()]
        sentinel = object()
        mock_dup.return_value = sentinel

        result = run_copy(resources={"workspace"}, reporter=NullReporter(), **_kwargs())

        self.assertIs(result, sentinel)
        mock_dup.assert_called_once()

    @patch("hexa.workspace_copier.service.copy_workspace")
    @patch("hexa.workspace_copier.service.build_client")
    def test_aborts_before_copy_on_bad_credentials(self, mock_build, mock_dup):
        mock_build.side_effect = GraphQLError("source authentication failed: bad")

        with self.assertRaises(CredentialError):
            run_copy(reporter=NullReporter(), **_kwargs())

        mock_dup.assert_not_called()


def _template_kwargs(**overrides):
    data = {
        "source_url": "http://src/graphql/",
        "source_token": "src-token",
        "target_url": "http://tgt/graphql/",
        "target_token": "tgt-token",
        "target_organization_id": "org-1",
    }
    data.update(overrides)
    return data


class RunTemplateCopyTest(SimpleTestCase):
    @patch("hexa.workspace_copier.service.copy_templates")
    @patch("hexa.workspace_copier.service.build_client")
    def test_proceeds_to_copy_after_successful_verification(
        self, mock_build, mock_copy
    ):
        mock_build.side_effect = [MagicMock(), MagicMock()]
        sentinel = object()
        mock_copy.return_value = sentinel

        result = run_template_copy(reporter=NullReporter(), **_template_kwargs())

        self.assertIs(result, sentinel)
        mock_copy.assert_called_once()

    @patch("hexa.workspace_copier.service.copy_templates")
    @patch("hexa.workspace_copier.service.build_client")
    def test_blank_url_is_a_credential_error_remote_only(self, mock_build, mock_copy):
        # Templates copy is remote→remote; a blank URL is rejected up front
        # rather than falling back to the local server.
        with self.assertRaises(CredentialError) as ctx:
            run_template_copy(
                reporter=NullReporter(), **_template_kwargs(source_url="")
            )

        self.assertIn("source server URL is required.", ctx.exception.errors)
        mock_copy.assert_not_called()

    @patch("hexa.workspace_copier.service.copy_templates")
    @patch("hexa.workspace_copier.service.build_client")
    def test_bad_credentials_abort_before_copy(self, mock_build, mock_copy):
        mock_build.side_effect = GraphQLError("source authentication failed: bad")

        with self.assertRaises(CredentialError):
            run_template_copy(reporter=NullReporter(), **_template_kwargs())

        mock_copy.assert_not_called()
