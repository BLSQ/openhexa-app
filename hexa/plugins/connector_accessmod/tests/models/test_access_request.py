from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessmodProfile,
    AccessRequest,
    AccessRequestStatus,
)
from hexa.user_management.models import User


class AccessRequestTest(TestCase):
    USER_SABRINA = None
    USER_MAX = None
    ACCESS_REQUEST_KIM = None
    ACCESS_REQUEST_JIM = None
    ACCESS_REQUEST_MARY = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        AccessmodProfile.objects.create(
            user=cls.USER_SABRINA, is_accessmod_superuser=True
        )

        cls.USER_MAX = User.objects.create_user(
            "max@bluesquarehub.com",
            "standardpassword",
        )

        cls.ACCESS_REQUEST_KIM = AccessRequest.objects.create(
            first_name="Kim",
            last_name="Jones",
            email="kimjones@bluesquarehub.com",
            accepted_tos=False,
            status=AccessRequestStatus.PENDING,
        )
        cls.ACCESS_REQUEST_JIM = AccessRequest.objects.create(
            first_name="Jim",
            last_name="Johnson",
            email="jimjohnson@bluesquarehub.com",
            accepted_tos=True,
            status=AccessRequestStatus.APPROVED,
        )
        cls.ACCESS_REQUEST_MARY = AccessRequest.objects.create(
            first_name="Mary",
            last_name="Jones",
            email="maryjones@bluesquarehub.com",
            accepted_tos=True,
            status=AccessRequestStatus.PENDING,
        )

    def test_create_access_request(self):
        with self.assertRaises(PermissionDenied):
            AccessRequest.objects.create_if_has_perm(
                self.USER_MAX,
                first_name="John",
                last_name="Doe",
                email="johndoe@openhexa.org",
                accepted_tos=True,
            )
        with self.assertRaises(ValidationError):
            AccessRequest.objects.create_if_has_perm(
                AnonymousUser(),
                first_name="John",
                last_name="Doe",
                email="johndoe@openhexa.org",
                accepted_tos=False,
            )

        access_request = AccessRequest.objects.create_if_has_perm(
            AnonymousUser(),
            first_name="John",
            last_name="Doe",
            email="johndoe@openhexa.org",
            accepted_tos=True,
        )
        self.assertIsInstance(access_request, AccessRequest)
        self.assertEqual(AccessRequestStatus.PENDING, access_request.status)

    def test_approve_access_request(self):
        with self.assertRaises(PermissionDenied):
            self.ACCESS_REQUEST_MARY.approve_if_has_perm(
                self.USER_MAX, request=self.mock_request(self.USER_MAX)
            )
        with self.assertRaises(ValidationError):
            self.ACCESS_REQUEST_JIM.approve_if_has_perm(
                self.USER_SABRINA, request=self.mock_request(self.USER_SABRINA)
            )
        with self.assertRaises(ValidationError):
            self.ACCESS_REQUEST_KIM.approve_if_has_perm(
                self.USER_SABRINA, request=self.mock_request(self.USER_SABRINA)
            )

        self.ACCESS_REQUEST_MARY.approve_if_has_perm(
            self.USER_SABRINA, request=self.mock_request(self.USER_SABRINA)
        )
        self.ACCESS_REQUEST_MARY.refresh_from_db()
        self.assertEqual(AccessRequestStatus.APPROVED, self.ACCESS_REQUEST_MARY.status)
        self.assertIsInstance(self.ACCESS_REQUEST_MARY.user, User)
        self.assertEqual(
            self.ACCESS_REQUEST_MARY.email, self.ACCESS_REQUEST_MARY.user.email
        )
        # The user has not accepted OpenHexa TOS, but the AccessMod TOS flag should be true
        accessmod_profile = AccessmodProfile.objects.get(
            user=self.ACCESS_REQUEST_MARY.user
        )
        self.assertTrue(accessmod_profile.accepted_tos)
        self.assertFalse(accessmod_profile.user.accepted_tos)

    def test_deny_access_request(self):
        with self.assertRaises(PermissionDenied):
            self.ACCESS_REQUEST_MARY.deny_if_has_perm(self.USER_MAX)
        with self.assertRaises(ValidationError):
            self.ACCESS_REQUEST_JIM.deny_if_has_perm(self.USER_SABRINA)

        self.ACCESS_REQUEST_MARY.deny_if_has_perm(self.USER_SABRINA)
        self.ACCESS_REQUEST_MARY.refresh_from_db()
        self.assertEqual(AccessRequestStatus.DENIED, self.ACCESS_REQUEST_MARY.status)
        self.assertIsNone(self.ACCESS_REQUEST_MARY.user)
