import uuid

from django.core.signing import Signer
from django.test import RequestFactory

from hexa.core.test import GraphQLTestCase
from hexa.user_management.middlewares import service_account_token_middleware
from hexa.user_management.models import (
    ServiceAccount,
    User,
)


class ServiceAccountModelTest(GraphQLTestCase):
    def test_create_service_account(self):
        svc = ServiceAccount.objects.create_user(
            "svc@openhexa.org",
            "password",
        )
        self.assertIsInstance(svc, ServiceAccount)
        self.assertIsInstance(svc, User)
        self.assertIsNotNone(svc.access_token)
        self.assertIsInstance(svc.access_token, uuid.UUID)

    def test_rotate_token_changes_value(self):
        svc = ServiceAccount.objects.create_user(
            "svc@openhexa.org",
            "password",
        )
        old_token = svc.access_token
        svc.rotate_token()
        svc.refresh_from_db()
        self.assertNotEqual(old_token, svc.access_token)


class ServiceAccountMiddlewareTest(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.svc = ServiceAccount.objects.create_user(
            "svc@openhexa.org",
            "password",
            is_active=True,
        )
        self.signed_token = Signer().sign_object(str(self.svc.access_token))

        self.get_response = lambda request: request
        self.middleware = service_account_token_middleware(self.get_response)

    def test_valid_token_authenticates(self):
        request = self.factory.get(
            "/", HTTP_AUTHORIZATION=f"Bearer {self.signed_token}"
        )
        request.user = None
        self.middleware(request)
        self.assertEqual(request.user.pk, self.svc.pk)

    def test_no_auth_header_passes_through(self):
        request = self.factory.get("/")
        request.user = "original"
        self.middleware(request)
        self.assertEqual(request.user, "original")

    def test_invalid_token_passes_through(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer invalid-token")
        request.user = "original"
        self.middleware(request)
        self.assertEqual(request.user, "original")

    def test_inactive_account_rejected(self):
        self.svc.is_active = False
        self.svc.save()
        request = self.factory.get(
            "/", HTTP_AUTHORIZATION=f"Bearer {self.signed_token}"
        )
        request.user = "original"
        self.middleware(request)
        self.assertEqual(request.user, "original")

    def test_regular_user_with_matching_uuid_rejected(self):
        User.objects.create_user(
            "regular@openhexa.org",
            "password",
            is_active=True,
        )
        token_value = uuid.uuid4()
        signed = Signer().sign_object(str(token_value))

        request = self.factory.get("/", HTTP_AUTHORIZATION=f"Bearer {signed}")
        request.user = "original"
        self.middleware(request)
        self.assertEqual(request.user, "original")
