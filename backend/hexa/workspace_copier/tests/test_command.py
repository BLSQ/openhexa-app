from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from hexa.workspace_copier.management.commands.copy_workspace import (
    Command,
    _known_resource_names,
)
from hexa.workspace_copier.results import CopyResult


class ResolveResourcesTest(SimpleTestCase):
    def setUp(self):
        self.command = Command()

    def test_empty_means_all(self):
        self.assertEqual(self.command._resolve_resources(None), _known_resource_names())

    def test_explicit_subset(self):
        self.assertEqual(
            self.command._resolve_resources("connections,files"),
            {"connections", "files"},
        )

    def test_unknown_resource_raises(self):
        with self.assertRaises(CommandError):
            self.command._resolve_resources("connections,bogus")


class ParseFoldersTest(SimpleTestCase):
    def test_empty_means_none(self):
        self.assertEqual(Command._parse_folders(None), set())
        self.assertEqual(Command._parse_folders(""), set())

    def test_parses_and_strips_slashes(self):
        self.assertEqual(
            Command._parse_folders("tmp, /cache/ ,output,"),
            {"tmp", "cache", "output"},
        )


class HandleValidationTest(SimpleTestCase):
    def _options(self, **overrides):
        opts = {
            "source_workspace_slug": "src",
            "source_url": "",
            "source_token": "",
            "target_url": "",
            "target_token": "",
            "target_organization": None,
            "target_workspace_name": None,
            "target_workspace_slug": None,
            "resources": None,
            "skip_folders": None,
            "only_folders": None,
        }
        opts.update(overrides)
        return opts

    def test_missing_org_without_slug_raises(self):
        with self.assertRaises(CommandError):
            Command().handle(**self._options())

    @patch("hexa.workspace_copier.management.commands.copy_workspace.run_copy")
    def test_slug_makes_org_optional_and_is_threaded(self, mock_run):
        mock_run.return_value = CopyResult(
            workspace_name="x", workspace_slug="existing-ws"
        )

        Command().handle(**self._options(target_workspace_slug="existing-ws"))

        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs["target_workspace_slug"], "existing-ws")

    @patch("hexa.workspace_copier.management.commands.copy_workspace.run_copy")
    def test_skip_folders_are_threaded(self, mock_run):
        mock_run.return_value = CopyResult(
            workspace_name="x", workspace_slug="existing-ws"
        )

        Command().handle(
            **self._options(
                target_workspace_slug="existing-ws", skip_folders="tmp,output"
            )
        )

        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs["skip_dirs"], {"tmp", "output"})
        self.assertIsNone(kwargs["only_dirs"])

    @patch("hexa.workspace_copier.management.commands.copy_workspace.run_copy")
    def test_only_folders_are_threaded(self, mock_run):
        mock_run.return_value = CopyResult(
            workspace_name="x", workspace_slug="existing-ws"
        )

        Command().handle(
            **self._options(
                target_workspace_slug="existing-ws", only_folders="notebooks,data"
            )
        )

        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs["only_dirs"], {"notebooks", "data"})
