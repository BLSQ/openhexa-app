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
