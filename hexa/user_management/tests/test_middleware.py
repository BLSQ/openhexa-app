from django.test import RequestFactory
from django_otp import DEVICE_ID_SESSION_KEY

from hexa.core.test import TestCase
from hexa.user_management.models import User

from ..middlewares import TwoFactorMiddleware


class TwoFactorMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )
        self.USER_JOE = User.objects.create_user(
            "joe@bluesquarehub.com",
            "joe's password",
        )

        self.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com", "Sabr!na"
        )

        for user in [self.USER_SERENA, self.USER_JOE]:
            device = user.staticdevice_set.create()
            device.token_set.create(token=user.get_username()[:10])

        self.middleware = TwoFactorMiddleware(lambda r: None)

    def test_verified(self):
        request = self.factory.get("/")
        request.user = self.USER_SERENA
        device = self.USER_SERENA.staticdevice_set.get()
        request.session = {DEVICE_ID_SESSION_KEY: device.persistent_id}

        self.middleware(request)

        self.assertTrue(request.user.is_verified())

    def test_enabled(self):
        request = self.factory.get("/")

        request.user = self.USER_SERENA
        device = self.USER_SERENA.staticdevice_set.get()

        request.session = {DEVICE_ID_SESSION_KEY: device.persistent_id}

        self.middleware(request)
        self.assertTrue(request.user.is_verified())

    def test_not_enabled(self):
        request = self.factory.get("/")

        request.user = self.USER_SABRINA
        request.session = {}

        self.middleware(request)
        self.assertFalse(request.user.is_verified())

    def test_verified_legacy_device_id(self):
        request = self.factory.get("/")
        request.user = self.USER_SERENA
        device = self.USER_SERENA.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: f"{device.__module__}.{device.__class__.__name__}/{device.id}"
        }

        self.middleware(request)

        self.assertTrue(request.user.is_verified())

    def test_unverified(self):
        request = self.factory.get("/")
        request.user = self.USER_SERENA
        request.session = {}

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_no_device(self):
        request = self.factory.get("/")
        request.user = self.USER_SERENA
        request.session = {
            DEVICE_ID_SESSION_KEY: "otp_static.staticdevice/0",
        }

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_no_model(self):
        request = self.factory.get("/")
        request.user = self.USER_SERENA
        request.session = {
            DEVICE_ID_SESSION_KEY: "otp_bogus.bogusdevice/0",
        }

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_wrong_user(self):
        request = self.factory.get("/")
        request.user = self.USER_SERENA
        device = self.USER_JOE.staticdevice_set.get()
        request.session = {DEVICE_ID_SESSION_KEY: device.persistent_id}

        self.middleware(request)

        self.assertFalse(request.user.is_verified())
