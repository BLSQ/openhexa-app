from io import StringIO

from django.core.management import call_command

from hexa.core.test import TestCase


class FixturesTest(TestCase):
    def test_fixtures(self):
        call_command("loaddata", "demo.json", stdout=StringIO())
