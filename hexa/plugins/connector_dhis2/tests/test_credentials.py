from django.urls import reverse

from hexa.core.test import TestCase
from hexa.plugins.connector_dhis2.models import (
    Credentials,
    Instance,
    InstancePermission,
)
from hexa.user_management.models import Membership, Team, User


class CredentialsTest(TestCase):
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
            "instance1,instance2,instance3",
            response_data["env"]["DHIS2_INSTANCES_SLUGS"],
        )

    def test_credentials_200_regular_user(self):
        """
        A regular should get credentials for the instances he has credentials
        permissions for. (instance1 and not instance2 or instance3)"""
        self.client.force_login(self.REGULAR_USER)
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            "instance1",
            response_data["env"]["DHIS2_INSTANCES_SLUGS"],
        )

        # REGULAR_USER has permission + enable_notebooks_credentials
        self.assertIn("DHIS2_INSTANCE1_PASSWORD", response_data["env"])

        # REGULAR_USER has permission but not enable_notebooks_credentials
        self.assertNotIn("DHIS2_INSTANCE2_PASSWORD", response_data["env"])

        # REGULAR_USER has no permission
        self.assertNotIn("DHIS2_INSTANCE3_PASSWORD", response_data["env"])
