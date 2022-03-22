import urllib.parse

from django import test
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.metrics.models import Request
from hexa.user_management.models import User


class MetricsTest(TestCase):
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
        req_count_1 = Request.objects.count()
        self.client.get(reverse("catalog:index"))
        req_count_2 = Request.objects.count()
        self.assertEqual(req_count_1 + 1, req_count_2)
        saved_request = Request.objects.get()
        self.assertEqual(saved_request.url, reverse("catalog:index"))
        self.assertEqual(saved_request.query_string, "")

    @test.override_settings(SAVE_REQUESTS=True)
    def test_save_request_querystring_simple(self):
        self.client.force_login(self.USER_FOO)
        self.client.get(
            f"{reverse('catalog:index')}?yo",
        )
        saved_request = Request.objects.get()
        self.assertEqual(saved_request.query_string, "yo")

    @test.override_settings(SAVE_REQUESTS=True)
    def test_save_request_querystring_multiple(self):
        self.client.force_login(self.USER_FOO)
        self.client.get(
            f"{reverse('catalog:index')}?foo=bar&bar=baz",
        )
        saved_request = Request.objects.get()
        self.assertEqual(saved_request.query_string, "foo=bar&bar=baz")

    @test.override_settings(SAVE_REQUESTS=True)
    def test_save_redirect(self):
        self.client.force_login(self.USER_FOO)
        req_count_1 = Request.objects.count()
        url = (
            reverse("metrics:save_redirect")
            + "?to="
            + urllib.parse.quote("https://some.site.invalid/page/", safe="")
        )
        response = self.client.get(url)
        req_count_2 = Request.objects.count()
        self.assertEqual(req_count_1 + 1, req_count_2)
        self.assertEqual(response.status_code, 302)
        url = Request.objects.order_by("-id").last().url
        self.assertEqual(url, "https://some.site.invalid/page/")

    @test.override_settings(SAVE_REQUESTS=True)
    def test_do_not_track(self):
        self.client.force_login(self.USER_FOO)
        req_count_1 = Request.objects.count()
        url = f"{reverse('metrics:save_redirect')}?to={urllib.parse.quote('https://some.site.invalid/page/', safe='')}"
        self.client.get(url)
        req_count_2 = Request.objects.count()
        self.assertEqual(req_count_1 + 1, req_count_2)
