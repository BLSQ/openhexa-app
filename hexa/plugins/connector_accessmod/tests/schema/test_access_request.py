from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import AccessRequest
from hexa.user_management.models import User


class AccessRequestTest(GraphQLTestCase):
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
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

    def test_signup_for_accessmod(self):
        r = self.run_query(
            """
              mutation requestAccessmodAccess($input: RequestAccessmodAccessInput!) {
                requestAccessmodAccess(input: $input) {
                  success
                }
              }
            """,
            {
                "input": {
                    "email": "wolfgang@bluesquarehub.com",
                    "firstName": "Wolfgang",
                    "lastName": "Müller",
                    "acceptTos": True,
                }
            },
        )

        self.assertEqual(
            {"success": True},
            r["data"]["requestAccessmodAccess"],
        )
        self.assertTrue(
            AccessRequest.objects.filter(email="wolfgang@bluesquarehub.com").exists()
        )

    def test_signup_for_accessmod_errors(self):
        # User hasn't accepted TOS
        r = self.run_query(
            """
              mutation requestAccessmodAccess($input: RequestAccessmodAccessInput!) {
                requestAccessmodAccess(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "email": "gunther@bluesquarehub.com",
                    "firstName": "Gunther",
                    "lastName": "Grass",
                    "acceptTos": False,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["MUST_ACCEPT_TOS"]},
            r["data"]["requestAccessmodAccess"],
        )

        # Email is already used
        r = self.run_query(
            """
              mutation requestAccessmodAccess($input: RequestAccessmodAccessInput!) {
                requestAccessmodAccess(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "email": "sabrina@bluesquarehub.com",
                    "firstName": "Sabrina",
                    "lastName": "Muller",
                    "acceptTos": True,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["ALREADY_EXISTS"]},
            r["data"]["requestAccessmodAccess"],
        )

        # Invalid email
        r = self.run_query(
            """
              mutation requestAccessmodAccess($input: RequestAccessmodAccessInput!) {
                requestAccessmodAccess(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "email": "notanemail",
                    "firstName": "Sabrina",
                    "lastName": "Muller",
                    "acceptTos": True,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID"]},
            r["data"]["requestAccessmodAccess"],
        )
