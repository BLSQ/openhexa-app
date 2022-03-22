from django.urls import reverse

from hexa.core.test import TestCase
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.pipelines.tests.test_credentials import BaseCredentialsTestCase
from hexa.plugins.connector_airflow.models import DAGAuthorizedDatasource
from hexa.plugins.connector_postgresql.credentials import pipelines_credentials
from hexa.plugins.connector_postgresql.models import Database, DatabasePermission
from hexa.user_management.models import Membership, Team, User


class NotebooksCredentialsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.SUPER_USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim2021__",
            is_superuser=True,
        )
        cls.REGULAR_USER = User.objects.create_user(
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
            "DB1,DB2",
            response_data["env"]["POSTGRESQL_DATABASE_NAMES"],
        )

    def test_credentials_200_regular_user(self):
        self.client.force_login(self.REGULAR_USER)
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            "DB1",
            response_data["env"]["POSTGRESQL_DATABASE_NAMES"],
        )


class PipelinesCredentialsTest(BaseCredentialsTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.DATABASE = Database.objects.create(
            hostname="localhost", username="user1", password="pass1", database="db1"
        )

    def test_single(self):
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.DATABASE
        )

        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        self.assertEqual(
            {
                "POSTGRESQL_DATABASE_NAMES": "DB1",
                "POSTGRESQL_DB1_DATABASE": "db1",
                "POSTGRESQL_DB1_HOSTNAME": "localhost",
                "POSTGRESQL_DB1_PASSWORD": "pass1",
                "POSTGRESQL_DB1_PORT": "5432",
                "POSTGRESQL_DB1_URL": "postgresql://user1:pass1@localhost:5432/db1",
                "POSTGRESQL_DB1_USERNAME": "user1",
            },
            credentials.env,
        )

    def test_slug(self):
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.DATABASE, slug="slug1"
        )

        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        self.assertEqual(
            {
                "POSTGRESQL_DATABASE_NAMES": "SLUG1",
                "POSTGRESQL_SLUG1_DATABASE": "db1",
                "POSTGRESQL_SLUG1_HOSTNAME": "localhost",
                "POSTGRESQL_SLUG1_PASSWORD": "pass1",
                "POSTGRESQL_SLUG1_PORT": "5432",
                "POSTGRESQL_SLUG1_URL": "postgresql://user1:pass1@localhost:5432/db1",
                "POSTGRESQL_SLUG1_USERNAME": "user1",
            },
            credentials.env,
        )
