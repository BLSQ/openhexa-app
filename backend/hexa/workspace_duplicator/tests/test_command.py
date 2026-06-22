from django.core.management.base import CommandError
from django.test import SimpleTestCase

from hexa.workspace_duplicator.management.commands.migrate_workspace import (
    Command,
    _known_resource_names,
)


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
