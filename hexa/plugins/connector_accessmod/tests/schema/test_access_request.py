from django.conf import settings
from django.core import mail

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessmodProfile,
    AccessRequest,
    AccessRequestStatus,
)
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
            status=AccessRequestStatus.APPROVED,
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
                    status
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
                    {
                        "id": str(self.ACCESS_REQUEST_NINA.id),
                        "status": self.ACCESS_REQUEST_NINA.status,
                    },
                    {
                        "id": str(self.ACCESS_REQUEST_JULIA.id),
                        "status": self.ACCESS_REQUEST_JULIA.status,
                    },
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
            AccessRequest.objects.filter(
                email="wolfgang@bluesquarehub.com", status=AccessRequestStatus.PENDING
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("has requested an access to AccessMod", mail.outbox[0].subject)
        self.assertIn(settings.ACCESSMOD_MANAGE_REQUESTS_URL, mail.outbox[0].body)

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
            {"success": False, "errors": ["INVALID"]},
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
            {"success": False, "errors": ["INVALID"]},
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

    def test_approve_accessmod_access_request(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
              mutation approveAccessmodAccessRequest($input: ApproveAccessmodAccessRequestInput!) {
                approveAccessmodAccessRequest(input: $input) {
                  success
                }
              }
            """,
            {
                "input": {
                    "id": str(self.ACCESS_REQUEST_JULIA.id),
                }
            },
        )

        self.assertEqual(
            {"success": True},
            r["data"]["approveAccessmodAccessRequest"],
        )
        self.ACCESS_REQUEST_JULIA.refresh_from_db()
        self.assertEqual(AccessRequestStatus.APPROVED, self.ACCESS_REQUEST_JULIA.status)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "Your AccessMod access request has been approved", mail.outbox[0].subject
        )
        self.assertIn(self.ACCESS_REQUEST_JULIA.email, mail.outbox[0].recipients())
        self.assertIn(settings.ACCESSMOD_SET_PASSWORD_URL, mail.outbox[0].body)

    def test_approve_accessmod_access_request_errors(self):
        # Rebecca is not an AccessMod superuser
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
              mutation approveAccessmodAccessRequest($input: ApproveAccessmodAccessRequestInput!) {
                approveAccessmodAccessRequest(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "id": str(self.ACCESS_REQUEST_NINA.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["INVALID"]},
            r["data"]["approveAccessmodAccessRequest"],
        )

        # Sabrina is an AccessMod superuser
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
              mutation approveAccessmodAccessRequest($input: ApproveAccessmodAccessRequestInput!) {
                approveAccessmodAccessRequest(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "id": str(self.ACCESS_REQUEST_NINA.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["INVALID"]},
            r["data"]["approveAccessmodAccessRequest"],
        )

    def test_deny_accessmod_access_request(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
              mutation denyAccessmodAccessRequest($input: DenyAccessmodAccessRequestInput!) {
                denyAccessmodAccessRequest(input: $input) {
                  success
                }
              }
            """,
            {
                "input": {
                    "id": str(self.ACCESS_REQUEST_JULIA.id),
                }
            },
        )

        self.assertEqual(
            {"success": True},
            r["data"]["denyAccessmodAccessRequest"],
        )
        self.ACCESS_REQUEST_JULIA.refresh_from_db()
        self.assertEqual(AccessRequestStatus.DENIED, self.ACCESS_REQUEST_JULIA.status)

    def test_deny_accessmod_access_request_errors(self):
        # Rebecca is not an AccessMod superuser
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
              mutation denyAccessmodAccessRequest($input: DenyAccessmodAccessRequestInput!) {
                denyAccessmodAccessRequest(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "id": str(self.ACCESS_REQUEST_NINA.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["INVALID"]},
            r["data"]["denyAccessmodAccessRequest"],
        )

        # Sabrina is an AccessMod superuser
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
              mutation denyAccessmodAccessRequest($input: DenyAccessmodAccessRequestInput!) {
                denyAccessmodAccessRequest(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "id": str(self.ACCESS_REQUEST_NINA.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["INVALID"]},
            r["data"]["denyAccessmodAccessRequest"],
        )
