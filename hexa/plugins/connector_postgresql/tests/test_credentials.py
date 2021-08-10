from django import test
from django.urls import reverse

from hexa.plugins.connector_postgresql.models import (
    Database,
    DatabasePermission,
)
from hexa.user_management.models import User, Team, Membership


class CredentialsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.SUPER_USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim@bluesquarehub.com",
            "jim2021__",
            is_superuser=True,
        )
        cls.REGULAR_USER = User.objects.create_user(
            "john@bluesquarehub.com",
            "john@bluesquarehub.com",
            "john2021__",
            is_superuser=False,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.REGULAR_USER)
        cls.DATABASE_1 = Database.objects.create(
            hostname="localhost", username="db1", password="db1", database="db1"
        )
        cls.DATABASE_2 = Database.objects.create(
            hostname="localhost", username="db2", password="db2", database="db2"
        )
        DatabasePermission.objects.create(database=cls.DATABASE_1, team=cls.TEAM)

    def test_credentials_200_super_user(self):
        self.client.force_login(self.SUPER_USER)
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            "db1,db2",
            response_data["env"]["POSTGRESQL_DATABASE_NAMES"],
        )

    def test_credentials_200_regular_user(self):
        self.client.force_login(self.REGULAR_USER)
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            "db1",
            response_data["env"]["POSTGRESQL_DATABASE_NAMES"],
        )
