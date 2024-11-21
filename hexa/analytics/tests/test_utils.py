from django.test import RequestFactory

from hexa.analytics.utils import get_ip_address
from hexa.core.test import TestCase


class TestUtils(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_get_ip_address(self):
        request = self.factory.post("/pipelines/")
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        self.assertEqual(get_ip_address(request), "127.0.0.1")

    def test_get_ip_address_forwarded(self):
        request = self.factory.post("/pipelines/")
        request.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.195, 192.168.1.1, 192.168.1.2"
        self.assertEqual(get_ip_address(request), "203.0.113.195")
