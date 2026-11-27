from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
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


class DisableSslVerificationFlagTest(SimpleTestCase):
    def _options(self, *extra_args):
        with patch(
            "hexa.workspace_copier.management.commands.copy_workspace.run_copy",
            return_value=CopyResult(),
        ) as mock_run:
            call_command(
                "copy_workspace",
                "--source-workspace-slug=src",
                "--target-organization=org",
                *extra_args,
                stdout=StringIO(),
            )
        return mock_run.call_args.kwargs["options"]

    def test_certificates_are_verified_by_default(self):
        self.assertTrue(self._options().verify_ssl)

    def test_flag_turns_verification_off(self):
        self.assertFalse(self._options("--disable-ssl-verification").verify_ssl)
