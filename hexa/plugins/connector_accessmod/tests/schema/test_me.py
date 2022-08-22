from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import AccessmodProfile
from hexa.user_management.models import User


class MeTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        AccessmodProfile.objects.create(
            user=cls.USER_SABRINA, is_accessmod_superuser=True
        )
        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )

    def test_me_authorized_actions(self):
        # Sabrina is an AccessMod superuser
        self.client.force_login(self.USER_SABRINA)

        r = self.run_query(
            """
              query me {
                me {
                  authorizedActions
                }
              }
            """
        )

        self.assertIn("CREATE_TEAM", r["data"]["me"]["authorizedActions"])
        self.assertIn("CREATE_ACCESSMOD_PROJECT", r["data"]["me"]["authorizedActions"])
        self.assertIn(
            "MANAGE_ACCESSMOD_ACCESS_REQUESTS", r["data"]["me"]["authorizedActions"]
        )

        # Rebecca is not an AccessMod superuser
        self.client.force_login(self.USER_REBECCA)

        r = self.run_query(
            """
              query me {
                me {
                  authorizedActions
                }
              }
            """
        )

        self.assertIn("CREATE_TEAM", r["data"]["me"]["authorizedActions"])
        self.assertIn("CREATE_ACCESSMOD_PROJECT", r["data"]["me"]["authorizedActions"])
        self.assertNotIn(
            "MANAGE_ACCESSMOD_ACCESS_REQUESTS", r["data"]["me"]["authorizedActions"]
        )
