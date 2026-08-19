from urllib.parse import parse_qs, urlparse

from django.test import RequestFactory

from hexa.core.test import TestCase
from hexa.webapps.utils import POWERED_BY_TARGET_URL, powered_by_url


class PoweredByUrlTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_builds_target_with_utm_params(self):
        request = self.factory.get("/", HTTP_HOST="my-app.webapps.test")
        url = powered_by_url(request, "static")

        parsed = urlparse(url)
        self.assertEqual(
            f"{parsed.scheme}://{parsed.netloc}{parsed.path}", POWERED_BY_TARGET_URL
        )
        params = parse_qs(parsed.query)
        self.assertEqual(params["utm_source"], ["openhexa-webapps"])
        self.assertEqual(params["utm_medium"], ["referral"])
        self.assertEqual(params["utm_campaign"], ["powered-by-openhexa-banner"])
        self.assertEqual(params["utm_content"], ["static"])
        self.assertEqual(params["utm_term"], ["my-app.webapps.test"])

    def test_surface_and_host_are_used_verbatim(self):
        request = self.factory.get("/", HTTP_HOST="data.ministry.example")
        url = powered_by_url(request, "iframe")
        self.assertIn("utm_source=openhexa-webapps", url)
        self.assertIn("utm_content=iframe", url)
        self.assertIn("utm_term=data.ministry.example", url)
