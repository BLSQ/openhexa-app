from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import User


class WorkspaceAdminChangelistTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.STAFF = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True, is_superuser=True
        )

    def setUp(self):
        self.client.force_login(self.STAFF)

    def test_changelists_can_be_filtered_and_searched(self):
        for model, params in (
            ("workspacemembership", {"role__exact": "ADMIN", "q": "jane"}),
            ("workspaceinvitation", {"status__exact": "PENDING", "q": "jane"}),
            ("connection", {"q": "dhis2"}),
        ):
            with self.subTest(model=model):
                response = self.client.get(
                    reverse(f"admin:workspaces_{model}_changelist"), params
                )
                self.assertEqual(response.status_code, 200)
