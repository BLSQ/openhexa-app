from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User


class ProjectTest(GraphQLTestCase):
    TEAM = None
    WATER_FILESET = None
    SAMPLE_PROJECT = None
    OTHER_PROJECT = None
    WATER_ROLE = None
    USER_JIM = None
    USER_JANE = None
    PERMISSION = None

    @classmethod
    def setUpTestData(cls):
        pass

    def test_signup_for_accessmod(self):
        r = self.run_query(
            """
              mutation signUpForAccessmod($input: SignUpForAccessmodInput!) {
                signUpForAccessmod(input: $input) {
                  success
                }
              }
            """,
            {
                "input": {
                    "email": "wolfgang@bluesquarehub.com",
                    "password": "wolfgangistnett",
                    "firstName": "Wolfgang",
                    "lastName": "Müller",
                    "acceptTos": True,
                }
            },
        )

        self.assertEqual(
            {"success": True},
            r["data"]["signUpForAccessmod"],
        )
        self.assertEqual(
            False, User.objects.get(email="wolfgang@bluesquarehub.com").is_active
        )
