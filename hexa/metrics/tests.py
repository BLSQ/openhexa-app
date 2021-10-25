from django import test
from django.urls import reverse

from hexa.metrics.models import Request
from hexa.user_management.models import User


class WebRequestsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_FOO = User.objects.create_user(
            "foo@bluesquarehub.com",
            "Foo Bar",
        )

    @test.override_settings(SAVE_REQUESTS=True)
    def test_save_request(self):
        self.client.force_login(self.USER_FOO)
        reqc1 = Request.objects.count()
        response = self.client.get(
            reverse(
                "catalog:index",
            ),
        )
        reqc2 = Request.objects.count()
        self.assertEqual(reqc1 + 1, reqc2)
