from io import StringIO

from django.core.management import call_command

from hexa.core.test import TestCase
from hexa.user_management.models import User


class FixturesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            "root@openhexa.org",
            "root",
        )

    def test_fixtures(self):
        call_command("loaddata", "base.json", stdout=StringIO())
        call_command("loaddata", "demo.json", stdout=StringIO())
