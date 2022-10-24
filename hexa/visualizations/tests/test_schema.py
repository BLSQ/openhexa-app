from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import Membership, Team, User
from hexa.visualizations.models import ExternalDashboard, ExternalDashboardPermission


class VisualizationTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )
        cls.TEAM = Team.objects.create(name="Test Team")
        Membership.objects.create(user=cls.USER_SABRINA, team=cls.TEAM)

        cls.VIZ = ExternalDashboard.objects.create(
            url="https://viz.url", picture="__OVERRIDE_TEST__"
        )
        ExternalDashboardPermission.objects.create(
            external_dashboard=cls.VIZ, team=cls.TEAM
        )

    def test_external_dashboard(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query getExternalDashboards {
                externalDashboards {
                    totalPages
                    totalItems
                    items {
                        id
                    }
                }
            }
            """
        )
        self.assertEqual(
            {"totalPages": 1, "totalItems": 1, "items": [{"id": str(self.VIZ.id)}]},
            r["data"]["externalDashboards"],
        )

    def test_external_dashboard_no_access(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            query getExternalDashboards {
                externalDashboards {
                    totalPages
                    totalItems
                    items {
                        id
                    }
                }
            }
            """
        )
        self.assertEqual(0, len(r["data"]["externalDashboards"]["items"]))

    def test_external_dashboard_by_id(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query getExternalDashboardById ($id: String!) {
                externalDashboard(id: $id) {
                    id
                    name
                    url
                    }
                }

            """,
            {"id": str(self.VIZ.id)},
        )

        self.assertEqual(
            {
                "id": str(self.VIZ.id),
                "name": "Untitled Dashboard",
                "url": "https://viz.url",
            },
            r["data"]["externalDashboard"],
        )
