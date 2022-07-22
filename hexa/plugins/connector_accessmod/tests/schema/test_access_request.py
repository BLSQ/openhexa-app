from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import AccessmodProfile, AccessRequest
from hexa.user_management.models import User


class AccessRequestTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None
    ACCESS_REQUEST_JULIA = None
    ACCESS_REQUEST_NINA = None

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

        cls.ACCESS_REQUEST_JULIA = AccessRequest.objects.create(
            first_name="Julia",
            last_name="Muller",
            email="julia@bluesquarehub.com",
            accepted_tos=True,
        )
        cls.ACCESS_REQUEST_NINA = AccessRequest.objects.create(
            first_name="Nina",
            last_name="Muller",
            email="nina@bluesquarehub.com",
            accepted_tos=True,
        )

    def test_accessmod_access_request(self):
        # Sabrina is an AccessMod superuser
        self.client.force_login(self.USER_SABRINA)

        r = self.run_query(
            """
              query accessmodAccessRequests {
                accessmodAccessRequests {
                  pageNumber
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
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.ACCESS_REQUEST_JULIA.id)},
                    {"id": str(self.ACCESS_REQUEST_NINA.id)},
                ],
            },
            r["data"]["accessmodAccessRequests"],
        )

        # Rebecca is not an AccessMod superuser
        self.client.force_login(self.USER_REBECCA)

        r = self.run_query(
            """
              query accessmodAccessRequests {
                accessmodAccessRequests {
                  pageNumber
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
            {"pageNumber": 1, "totalPages": 1, "totalItems": 0, "items": []},
            r["data"]["accessmodAccessRequests"],
        )

    def test_request_accessmod_access(self):
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

    def test_request_accessmod_access_errors(self):
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
