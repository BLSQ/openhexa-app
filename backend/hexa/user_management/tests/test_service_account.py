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
        self.assertEqual(svc.token_hash, "")

    def test_generate_token(self):
        svc = ServiceAccount.objects.create_user(
            "svc@openhexa.org",
            "password",
        )
        raw_token = svc.generate_token()
        self.assertEqual(len(raw_token), 43)
        self.assertEqual(len(svc.token_hash), 64)
        self.assertEqual(svc.token_hash, ServiceAccount.hash_token(raw_token))

    def test_rotate_token_changes_value(self):
        svc = ServiceAccount.objects.create_user(
            "svc@openhexa.org",
            "password",
        )
        svc.generate_token()
        svc.save()
        old_hash = svc.token_hash
        svc.rotate_token()
        svc.refresh_from_db()
        self.assertNotEqual(old_hash, svc.token_hash)

    def test_hash_token_static(self):
        token = "test-token-value"
        hash1 = ServiceAccount.hash_token(token)
        hash2 = ServiceAccount.hash_token(token)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)


class ServiceAccountMiddlewareTest(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.svc = ServiceAccount.objects.create_user(
            "svc@openhexa.org",
            "password",
            is_active=True,
        )
        self.raw_token = self.svc.generate_token()
        self.svc.save()

        self.get_response = lambda request: request
        self.middleware = service_account_token_middleware(self.get_response)

    def test_valid_token_authenticates(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION=f"Bearer {self.raw_token}")
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
        request = self.factory.get("/", HTTP_AUTHORIZATION=f"Bearer {self.raw_token}")
        request.user = "original"
        self.middleware(request)
        self.assertEqual(request.user, "original")

    def test_regular_user_with_matching_token_rejected(self):
        User.objects.create_user(
            "regular@openhexa.org",
            "password",
            is_active=True,
        )
        fake_token = "some-random-token-value"

        request = self.factory.get("/", HTTP_AUTHORIZATION=f"Bearer {fake_token}")
        request.user = "original"
        self.middleware(request)
        self.assertEqual(request.user, "original")
