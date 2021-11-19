import urllib.parse

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
            accepted_tos=True,
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

    @test.override_settings(SAVE_REQUESTS=True)
    def test_save_redirect(self):
        self.client.force_login(self.USER_FOO)
        reqc1 = Request.objects.count()
        url = (
            reverse("metrics:save_redirect")
            + "?to="
            + urllib.parse.quote("https://some.site.invalid/page/", safe="")
        )
        response = self.client.get(url)
        reqc2 = Request.objects.count()
        self.assertEqual(reqc1 + 1, reqc2)
        self.assertEqual(response.status_code, 302)
        url = Request.objects.order_by("-id").last().url
        self.assertEqual(url, "https://some.site.invalid/page/")
