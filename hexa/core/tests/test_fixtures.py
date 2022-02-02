from io import StringIO

from django import test
from django.core.management import call_command


class FixturesTest(test.TestCase):
    def test_fixtures(self):
        call_command("loaddata", "demo.json", stdout=StringIO())
