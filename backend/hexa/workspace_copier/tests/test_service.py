from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase, override_settings

from hexa.core.test import TestCase
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.service import (
    CredentialError,
    _verify_endpoints,
    _verify_side,
    run_copy,
    run_template_copy,
)
from hexa.workspace_copier.transport import GraphQLError
from hexa.workspaces.tests.testutils import create_workspace


def _kwargs(**overrides):
    """Both sides on other servers by default, so verification never touches the DB."""
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
        endpoint = MagicMock()
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
    def test_unknown_source_slug_aborts_verification(self, mock_build):
        # The copiers read an absent source workspace as an empty one, so this
        # has to fail here rather than come back as a run that copied nothing.
        src_client = MagicMock()
        src_client.workspace.return_value = None
        mock_build.side_effect = [src_client, MagicMock()]

        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs())

        self.assertEqual(ctx.exception.errors, ["source workspace 'my-ws' not found"])

    @patch("hexa.workspace_copier.service.build_client")
    def test_success_returns_both_endpoints(self, mock_build):
        src_client, tgt_client = MagicMock(), MagicMock()
        mock_build.side_effect = [src_client, tgt_client]

        source, target = _verify_endpoints(**_kwargs())

        self.assertIs(source.client, src_client)
        self.assertEqual(source.slug, "my-ws")
        self.assertIs(source.workspace, src_client.workspace.return_value)
        self.assertIs(target.client, tgt_client)
        self.assertEqual(target.organization_id, "org-1")


class ExistingTargetTest(SimpleTestCase):
    """``target_workspace_slug``: look the workspace up instead of creating it."""

    @patch("hexa.workspace_copier.service.build_client")
    def test_existing_slug_builds_a_target_pointing_at_it(self, mock_build):
        src_client, tgt_client = MagicMock(), MagicMock()
        mock_build.side_effect = [src_client, tgt_client]

        _source, target = _verify_endpoints(**_kwargs(target_workspace_slug="live-ws"))

        tgt_client.workspace.assert_called_once_with(slug="live-ws")
        self.assertEqual(target.slug, "live-ws")
        # Stashed so the workspace copier reuses it instead of fetching again.
        self.assertIs(target.workspace, tgt_client.workspace.return_value)
        # The organization/name only apply when creating: with the slug set, the
        # workspace-metadata copier skips creation entirely.
        self.assertIsNone(target.organization_id)
        self.assertIsNone(target.workspace_name)

    @patch("hexa.workspace_copier.service.build_client")
    def test_unknown_slug_aborts_verification(self, mock_build):
        tgt_client = MagicMock()
        tgt_client.workspace.return_value = None
        mock_build.side_effect = [MagicMock(), tgt_client]

        with self.assertRaises(CredentialError) as ctx:
            _verify_endpoints(**_kwargs(target_workspace_slug="missing-ws"))

        self.assertEqual(len(ctx.exception.errors), 1)
        self.assertIn(
            "target workspace 'missing-ws' not found", ctx.exception.errors[0]
        )


@override_settings(INTERNAL_BASE_URL="http://app:8000")
class BlankUrlTest(SimpleTestCase):
    @patch("hexa.workspace_copier.service.build_client")
    def test_blank_urls_reach_this_server_over_graphql(self, mock_build):
        mock_build.side_effect = [MagicMock(), MagicMock()]

        _verify_endpoints(**_kwargs(source_url="", target_url=""))

        urls = [call.args[0] for call in mock_build.call_args_list]
        self.assertEqual(urls, ["http://app:8000/graphql/"] * 2)

    @patch("hexa.workspace_copier.service.build_client")
    def test_blank_target_url_can_create_a_new_workspace(self, mock_build):
        tgt_client = MagicMock()
        mock_build.side_effect = [MagicMock(), tgt_client]

        _source, target = _verify_endpoints(**_kwargs(target_url=""))

        self.assertIs(target.client, tgt_client)
        self.assertEqual(target.organization_id, "org-1")


OTHER_SERVER_ORG = "9f1c2c4e-0000-4000-8000-000000000000"


def _client(organization_id=None, can_update=True):
    """A client whose workspace is in ``organization_id`` (None: no workspace)."""
    client = MagicMock()
    client.organization_id = organization_id
    client.workspace.return_value.permissions.update = can_update
    return client


def _fake_gql(client, query, variables=None, operation_name=None):
    organization = {"id": client.organization_id} if client.organization_id else None
    return {"workspace": {"organization": organization} if organization else None}


@patch("hexa.workspace_copier.service.gql", _fake_gql)
@patch("hexa.workspace_copier.service.build_client")
class SameServerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.SOURCE = create_workspace(name="My ws", slug="my-ws", db_name="my_ws")
        cls.TARGET = create_workspace(name="Live ws", slug="live-ws", db_name="live_ws")

    def _verify(self, **overrides):
        return _verify_endpoints(same_server=True, **_kwargs(**overrides))

    def _here(self, workspace, **kwargs):
        return _client(str(workspace.organization_id), **kwargs)

    def _errors(self, **overrides):
        with self.assertRaises(CredentialError) as ctx:
            self._verify(**overrides)
        return ctx.exception.errors

    def test_workspaces_on_this_server_pass(self, mock_build):
        mock_build.side_effect = [self._here(self.SOURCE), self._here(self.TARGET)]

        source, target = self._verify(target_workspace_slug="live-ws")

        self.assertEqual(source.slug, "my-ws")
        self.assertEqual(target.slug, "live-ws")

    def test_new_target_in_an_organization_on_this_server_passes(self, mock_build):
        mock_build.side_effect = [self._here(self.SOURCE), _client()]

        self._verify(target_organization_id=str(self.TARGET.organization_id))

    def test_workspace_missing_from_this_server_aborts(self, mock_build):
        mock_build.side_effect = [_client(OTHER_SERVER_ORG), _client(OTHER_SERVER_ORG)]

        errors = self._errors(source_slug="elsewhere", target_workspace_slug="gone")

        self.assertEqual(
            errors,
            [
                "source: workspace 'elsewhere' is not on this server, so it cannot "
                "be copied as a same-server copy.",
                "target: workspace 'gone' is not on this server, so it cannot be "
                "copied as a same-server copy.",
            ],
        )

    def test_same_slug_on_another_server_aborts(self, mock_build):
        # "live-ws" exists here too, but the URL's workspace is in an
        # organization this server does not have.
        mock_build.side_effect = [
            self._here(self.SOURCE),
            _client(OTHER_SERVER_ORG),
        ]

        errors = self._errors(target_workspace_slug="live-ws")

        self.assertEqual(
            errors,
            [
                "target: workspace 'live-ws' is not on this server, so it cannot be "
                "copied as a same-server copy."
            ],
        )

    def test_new_target_in_an_organization_elsewhere_aborts(self, mock_build):
        mock_build.side_effect = [self._here(self.SOURCE), _client()]

        errors = self._errors(target_organization_id="not-a-uuid")

        self.assertEqual(
            errors,
            [
                "target: organization 'not-a-uuid' is not on this server, so it "
                "cannot be copied as a same-server copy."
            ],
        )

    def test_target_the_token_cannot_edit_aborts(self, mock_build):
        mock_build.side_effect = [
            self._here(self.SOURCE),
            self._here(self.TARGET, can_update=False),
        ]

        errors = self._errors(target_workspace_slug="live-ws")

        self.assertEqual(
            errors,
            [
                "target: this token cannot edit workspace 'live-ws' (it needs the "
                "editor role or above)."
            ],
        )

    def test_failed_sides_are_not_checked_again(self, mock_build):
        mock_build.side_effect = [
            GraphQLError("source authentication failed: bad"),
            self._here(self.TARGET),
        ]

        errors = self._errors(target_workspace_slug="live-ws")

        self.assertEqual(errors, ["source authentication failed: bad"])

    @patch("hexa.workspace_copier.service.copy_workspace")
    def test_run_copy_checks_when_the_option_is_set(self, mock_dup, mock_build):
        mock_build.side_effect = [_client(OTHER_SERVER_ORG), _client()]

        with self.assertRaises(CredentialError):
            run_copy(
                reporter=NullReporter(),
                options=CopyOptions(same_server=True),
                **_kwargs(source_slug="elsewhere"),
            )

        mock_dup.assert_not_called()


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
