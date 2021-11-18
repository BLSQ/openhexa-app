from django import test
from django.urls import reverse

from hexa.user_management.models import Membership, Team, User

from .models import ExternalDashboard, ExternalDashboardPermission


class ExternalDashboardTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_NOTEAM = User.objects.create_user(
            "noteam@bluesquarehub.com",
            "noteam",
            accepted_tos=True,
        )
        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
            accepted_tos=True,
        )
        Membership.objects.create(user=cls.USER_BJORN, team=cls.TEAM)
        cls.DASHBOARD = ExternalDashboard.objects.create(
            url="https://viz.company.invalid/", picture="__OVERRIDE_TEST__"
        )
        ExternalDashboardPermission.objects.create(
            external_dashboard=cls.DASHBOARD, team=cls.TEAM
        )

    def test_empty_index_dashboard(self):
        """no team user cant see the list of dashboard"""
        self.client.force_login(self.USER_NOTEAM)

        response = self.client.get(reverse("dashboards:dashboard_index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dashboard_indexes"].count(), 0)

    def test_index_dashboard(self):
        """Bjorn can see the list of dashboard"""
        self.client.force_login(self.USER_BJORN)

        response = self.client.get(reverse("dashboards:dashboard_index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dashboard_indexes"].count(), 1)

    def test_dashboard_detail_noteam(self):
        """As a no team user, you cant access an existing dashboard."""

        self.client.force_login(self.USER_NOTEAM)
        response = self.client.get(
            reverse(
                "dashboards:dashboard_detail",
                kwargs={"dashboard_id": self.DASHBOARD.id},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_dashboard_detail_bjorn(self):
        """As a team member, bjorn can see a dashboard detail"""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "dashboards:dashboard_detail",
                kwargs={"dashboard_id": self.DASHBOARD.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["dashboard"], ExternalDashboard)

    def test_dashboard_image_bjorn(self):
        """As a team member, bjorn can see a dashboard screenshot"""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "dashboards:dashboard_image",
                kwargs={"dashboard_id": self.DASHBOARD.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
