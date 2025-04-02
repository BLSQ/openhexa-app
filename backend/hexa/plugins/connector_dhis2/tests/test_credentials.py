from django.urls import reverse

from hexa.core.test import TestCase
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.pipelines.tests.test_credentials import BaseCredentialsTestCase
from hexa.plugins.connector_airflow.models import DAGAuthorizedDatasource
from hexa.plugins.connector_dhis2.credentials import pipelines_credentials
from hexa.plugins.connector_dhis2.models import (
    Credentials,
    Instance,
    InstancePermission,
)
from hexa.user_management.models import Membership, Team, User


class NotebookCredentialsTest(TestCase):
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
        cls.INSTANCE_1 = Instance.objects.create(
            url="localhost",
            slug="instance1",
            api_credentials=Credentials.objects.create(
                username="instance1", password="instance1"
            ),
        )
        cls.INSTANCE_2 = Instance.objects.create(
            url="localhost",
            slug="instance2",
            api_credentials=Credentials.objects.create(
                username="instance2", password="instance2"
            ),
        )
        cls.INSTANCE_3 = Instance.objects.create(
            url="localhost",
            slug="instance3",
            api_credentials=Credentials.objects.create(
                username="instance3", password="instance3"
            ),
        )
        InstancePermission.objects.create(
            instance=cls.INSTANCE_1, team=cls.TEAM, enable_notebooks_credentials=True
        )
        InstancePermission.objects.create(instance=cls.INSTANCE_2, team=cls.TEAM)

    def test_credentials_200_super_user(self):
        self.client.force_login(self.SUPER_USER)
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            "INSTANCE1,INSTANCE2,INSTANCE3",
            response_data["env"]["DHIS2_INSTANCES_SLUGS"],
        )

    def test_credentials_200_regular_user(self):
        """
        A regular should get credentials for the instances he has credentials
        permissions for. (instance1 and not instance2 or instance3)
        """
        self.client.force_login(self.REGULAR_USER)
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            "INSTANCE1",
            response_data["env"]["DHIS2_INSTANCES_SLUGS"],
        )

        # REGULAR_USER has permission + enable_notebooks_credentials
        self.assertIn("DHIS2_INSTANCE1_PASSWORD", response_data["env"])

        # REGULAR_USER has permission but not enable_notebooks_credentials
        self.assertNotIn("DHIS2_INSTANCE2_PASSWORD", response_data["env"])

        # REGULAR_USER has no permission
        self.assertNotIn("DHIS2_INSTANCE3_PASSWORD", response_data["env"])


class PipelinesCredentialsTest(BaseCredentialsTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.INSTANCE = Instance.objects.create(
            url="https://dhis2.example.com",
            api_credentials=Credentials.objects.create(
                api_url="https://dhis2.example.com",
                username="test_username",
                password="test_password",
            ),
            verbose_sync=True,
            slug="play",
        )

    def test_single(self):
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.INSTANCE
        )

        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        self.assertEqual(
            {
                "DHIS2_INSTANCES_SLUGS": "PLAY",
                "DHIS2_PLAY_PASSWORD": "test_password",
                "DHIS2_PLAY_URL": "https://dhis2.example.com",
                "DHIS2_PLAY_USERNAME": "test_username",
            },
            credentials.env,
        )

    def test_slug(self):
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.INSTANCE, slug="slug1"
        )

        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        self.assertEqual(
            {
                "DHIS2_INSTANCES_SLUGS": "SLUG1",
                "DHIS2_SLUG1_PASSWORD": "test_password",
                "DHIS2_SLUG1_URL": "https://dhis2.example.com",
                "DHIS2_SLUG1_USERNAME": "test_username",
            },
            credentials.env,
        )
